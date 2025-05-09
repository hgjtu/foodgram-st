from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_subscribed",
    )
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_active", "is_subscribed")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name",
                                      "last_name", "email", "avatar")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff",
                        "is_superuser", "is_subscribed")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Additional info",
            {"fields": ("shopping_cart", "favorites", "subscriptions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
