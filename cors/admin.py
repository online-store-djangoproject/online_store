from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm,UserCreationForm
from .models import User


# Register your models here.


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ['email']
    list_display = ['email','id', 'phone','first_name','last_name','is_active','is_staff','created_at']
    search_fields = ['phone']
    readonly_fields = ['last_login']
    filter_horizontal = ['groups','user_permissions']

    fieldsets = (
        ('Main', {'fields':('first_name','last_name','phone', 'email','password')}),
        ('permissions',{'fields':('is_active','is_staff','is_superuser','groups','last_login','user_permissions')}),
    )

    add_fieldsets = (
        (None, {'fields':('first_name','last_name','phone','email','password1','password2')}),
    )



    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


admin.site.register(User,UserAdmin)