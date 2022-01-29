from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from baseuser.models import User
from django.utils.translation import gettext_lazy as _
# Register your models here.


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fileds': ('phone_number',)})
    )

    list_display = ['username', 'email', 'is_staff']


admin.site.register(User, MyUserAdmin)

