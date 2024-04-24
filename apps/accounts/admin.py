from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm

    list_display = ('username', 'birth_date', 'phone_number', 'email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'slug')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name', 'bio',
            'birth_date',
            'phone_number',
            'avatar',
            'is_online'
        )
        }),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'slug'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(CustomUser, CustomUserAdmin)
