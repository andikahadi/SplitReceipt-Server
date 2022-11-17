from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NewUser


class AccountAdmin(UserAdmin):
    list_display = ('email', 'user_name', 'first_name', 'date_joined',
                    'last_login', 'is_active','is_admin', 'is_superuser', 'is_staff')
    search_fields = ('email', 'user_name', 'first_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('email',)

    filter_horizontal = ()
    list_filter = ()

    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'user_name', 'date_joined',
                           'last_login')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'user_name', 'password1', 'password2')
        }),
    )


admin.site.register(NewUser, AccountAdmin)