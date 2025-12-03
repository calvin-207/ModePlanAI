from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from system.models import Users


class JWTAuthentication(BaseJWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise exceptions.AuthenticationFailed(
                "Token contained no recognizable user identification",
                code="token_no_user_id",
            )

        user_model = get_user_model()
        try:
            user = user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "User not found", code="user_not_found"
            )

        if not getattr(user, "is_active", True):
            raise exceptions.AuthenticationFailed(
                "User is inactive", code="user_inactive"
            )

        # 查询用户；
        user.system_user = Users.objects.get(id = user.system_user_id)
        return user

