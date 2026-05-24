from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import UserManager
from django.core.validators import RegexValidator



# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True,verbose_name="Email")
    # username = models.CharField(max_length=50, unique=True, verbose_name="Username")
    phone_regex = RegexValidator(regex=r'^(0|0098|\+98)?9(0[1-5]|[1-3]\d|2[0-2]|9[0-9])\d{7}$',
                                 message='The entered phone number format is incorrect.')
    phone = models.CharField(validators=[phone_regex], max_length=11, blank=True, verbose_name="Phone number")
    first_name = models.CharField(verbose_name="First Name", max_length=30, blank=True)
    last_name = models.CharField(verbose_name="Last Name", max_length=30, blank=True)
    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.email},{self.phone},{self.get_full_name()}'


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
