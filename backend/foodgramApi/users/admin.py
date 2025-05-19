from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import User


class BaseHasRelationFilter(admin.SimpleListFilter):
    LOOKUP_CHOICES = (
        ("yes", _("Да")),
        ("no", _("Нет")),
    )
    relation_field = None  # Должно быть переопределено в подклассах

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(**{f"{self.relation_field}__isnull": False}).distinct()
        if self.value() == "no":
            return queryset.filter(**{f"{self.relation_field}__isnull": True}).distinct()
        return queryset
    

class UserHasRecipesFilter(BaseHasRelationFilter):
    title = _("есть рецепты")
    parameter_name = "has_recipes"
    relation_field = "recipes"


class UserHasSubscriptionsFilter(BaseHasRelationFilter):
    title = _("есть подписки")
    parameter_name = "has_subscriptions"
    relation_field = "subscriptions"


class UserHasSubscribersFilter(BaseHasRelationFilter):
    title = _("есть подписчики")
    parameter_name = "has_subscribers"
    relation_field = "subscribers"


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
                        "is_superuser")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Additional info",
            {"fields": ("shopping_cart", "favorites")},
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
    def get_full_name(self, user):
        return f"{user.first_name} {user.last_name}"

    @admin.display(description="Аватар")
    def get_avatar_preview(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" width="50" height="50" />')
        return "Нет аватара"

    @admin.display(description="Рецептов")
    def get_recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description="Подписок")
    def get_subscriptions_count(self, user):
        return user.following.count()

    @admin.display(description="Подписчиков")
    def get_subscribers_count(self, user):
        return user.followers.count()
