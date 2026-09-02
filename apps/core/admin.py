from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.core.models import User, UserFunctionPermission


class UserFunctionPermissionInline(admin.TabularInline):
    model = UserFunctionPermission
    fk_name = "user"
    extra = 0
    fields = ("function", "can_view", "can_create", "can_edit", "can_delete", "active")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    inlines = [UserFunctionPermissionInline]
    filter_horizontal = ()
    list_display = ("email", "full_name", "role", "area", "is_staff", "is_superuser", "active")
    list_filter = ("role", "is_staff", "is_superuser", "active")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("full_name", "role", "area", "company_id")}),
        (
            "Permissões",
            {"fields": ("is_active", "is_staff", "is_superuser", "active")},
        ),
        ("Datas", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "area",
                    "company_id",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ("last_login",)


@admin.register(UserFunctionPermission)
class UserFunctionPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "function",
        "can_view",
        "can_create",
        "can_edit",
        "can_delete",
        "active",
    )
    list_filter = ("function", "active")
    search_fields = ("user__email", "function")
