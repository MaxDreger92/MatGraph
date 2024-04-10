from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usermanagement.models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_approved')
    list_filter = ('is_staff', 'is_active', 'is_approved')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_approved', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)



