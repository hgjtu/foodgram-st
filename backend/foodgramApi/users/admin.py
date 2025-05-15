from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import User


class UserHasRecipesFilter(admin.SimpleListFilter):
    title = _("есть рецепты")
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Да")),
            ("no", _("Нет")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True).distinct()
        return queryset


class UserHasSubscriptionsFilter(admin.SimpleListFilter):
    title = _("есть подписки")
    parameter_name = "has_subscriptions"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Да")),
            ("no", _("Нет")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(subscriptions__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(subscriptions__isnull=True).distinct()
        return queryset


class UserHasSubscribersFilter(admin.SimpleListFilter):
    title = _("есть подписчики")
    parameter_name = "has_subscribers"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Да")),
            ("no", _("Нет")),
        )

    def queryset(self, request, queryset):
        # Assuming 'subscribers' is the related_name from the model that subscribes to User
        # For example, if a Subscription model has a ForeignKey 'subscribed_to' to User,
        # and User has a related_name 'subscribers'
        if self.value() == "yes":
            return queryset.filter(subscribers__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(subscribers__isnull=True).distinct()
        return queryset


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "get_full_name",
        "email",
        "get_avatar_preview",
        "get_recipes_count",
        "get_subscriptions_count",
        "get_subscribers_count",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = (
        "is_staff",
        "is_active",
        "is_subscribed",
        UserHasRecipesFilter,
        UserHasSubscriptionsFilter,
        UserHasSubscribersFilter,
    )
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

    @admin.display(description="ФИО")
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Аватар")
    @mark_safe
    def get_avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return "Нет аватара"

    @admin.display(description="Рецептов")
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description="Подписок")
    def get_subscriptions_count(self, obj):
        return obj.subscriptions.count()

    @admin.display(description="Подписчиков")
    def get_subscribers_count(self, obj):
        return obj.subscribers.count()
