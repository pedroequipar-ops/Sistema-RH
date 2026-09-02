from rest_framework import serializers

from apps.core.models import User, UserFunctionPermission


class UserFunctionPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFunctionPermission
        fields = ["function", "can_view", "can_create", "can_edit", "can_delete"]


class UserMeSerializer(serializers.ModelSerializer):
    function_permissions = UserFunctionPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "area",
            "company_id",
            "is_superuser",
            "function_permissions",
        ]
