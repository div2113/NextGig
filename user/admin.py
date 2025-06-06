from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_employer",
        "date_joined",
        "is_active",
    )
    search_fields = ("username", "email")
    list_filter = ("username", "first_name", "last_name", "is_employer")
