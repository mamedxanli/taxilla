from django.contrib import admin
from django.contrib.auth import get_user_model
from accounts.forms import TaxillaUserForm
from django.contrib.auth.admin import UserAdmin



@admin.register(get_user_model())
class TaxillaUserAdmin(UserAdmin):
    form = TaxillaUserForm
    UserAdmin.fieldsets += (
        ("Additional info", {
            'fields': (
                'employee_id',
                'company',
                'phone',
                'title',
                'location',
                'is_driver',
                'vip',
            )
        }),
    )

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'company',
        'phone',
        'is_driver',
        'is_staff',
    )

    UserAdmin.list_filter += ('is_driver', 'company')
