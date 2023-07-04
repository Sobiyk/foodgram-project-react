from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name',
                    'role')


admin.site.register(User, UserAdmin)
