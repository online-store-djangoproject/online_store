from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from cors.models import User


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=80, default="آدرس اصلی")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    full_address = models.TextField()
    postalcode_regex = RegexValidator(r"^\d{10}$", message="Enter a valid zipcode.")
    postal_code = models.CharField(max_length=10, validators=[postalcode_regex])
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]

    def __str__(self):
        return f"{self.user.email}, {self.title}, {self.city}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)


class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discount_codes", null=True, blank=True)
    percentage = models.PositiveSmallIntegerField(default=15)
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="used_discount_codes", null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        owner = self.user.email if self.user else "همه کاربران"
        return f"{self.code} - {owner}"

    def can_be_used_by(self, user):
        if not self.is_active or self.is_used:
            return False
        if self.user_id and self.user_id != user.id:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
