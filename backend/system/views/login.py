# -*- coding: utf-8 -*-
import base64
import random
from datetime import datetime, timedelta
from captcha.views import CaptchaStore, captcha_image
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from system.views.dept import DeptViewSet
from tenants.models import GlobalUsers
from utils.apiview import CustomAPIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from system.models import Users
from utils.jsonResponse import DetailResponse, ErrorResponse
from utils.request_util import save_login_log
from django_redis import get_redis_connection
from django.conf import settings
from config import IS_SINGLE_TOKEN
from system.views.system_config import getSystemConfig
from django.utils import timezone


class CaptchaView(CustomAPIView):
    """
    获取图片验证码
    """

    authentication_classes = []

    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
        imgage = captcha_image(request, hashkey)
        # 将图片转换为base64
        image_base = base64.b64encode(imgage.content)
        json_data = {
            "key": id,
            "image_base": "data:image/png;base64," + image_base.decode("utf-8"),
        }
        return DetailResponse(data=json_data)


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    """

    captcha = serializers.CharField(max_length=6)

    @classmethod
    def get_token(cls, user):
        refresh = super(LoginSerializer, cls).get_token(user)
        data = {}
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {"no_active_account": _("该账号已被禁用,请联系管理员")}


class LoginView(CustomAPIView):
    """
    登录接口
    """

    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer  # 显式声明序列化器

    # 删除验证码
    def delete_expire_captcha(self):
        five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
        CaptchaStore.objects.filter(expiration__lte=five_minute_ago).delete()

    def post(self, request):
        username = request.data.get("username", None)
        # 这个密码要混淆下
        password = request.data.get("password", None)
        captchaKey = request.data.get("captchaKey", None)
        captcha = request.data.get("captcha", None)

        open_capche = True
        capche_config = getSystemConfig(key="base.loginCaptcha", group=False)
        if capche_config:
            open_capche = capche_config.get("loginCaptcha", True)

        if open_capche:
            image_code = CaptchaStore.objects.filter(id=captchaKey).first()
            five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if image_code and five_minute_ago > image_code.expiration:
                self.delete_expire_captcha()
                msg = "验证码过期"
                save_login_log(request=request, status=False, msg=msg)
                return ErrorResponse(msg=msg)
            else:
                if image_code and (
                    image_code.response == captcha or image_code.challenge == captcha
                ):
                    image_code and image_code.delete()
                else:
                    self.delete_expire_captcha()
                    msg = "图片验证码错误"
                    save_login_log(request=request, status=False, msg=msg)
                    return ErrorResponse(msg=msg)

        globalUsers = GlobalUsers.objects.filter(username=username).first()

        if not globalUsers:
            return ErrorResponse(msg="账号/密码错误")

        if globalUsers and not globalUsers.is_active:
            msg = "该账号已被禁用"
            save_login_log(request=request, status=False, msg=msg, user=globalUsers)
            return ErrorResponse(msg=msg)
        if globalUsers and globalUsers.check_password(
            password
        ):  # check_password() 对明文进行加密,并验证
            data = LoginSerializer.get_token(globalUsers)
            msg = "登录成功"
            globalUsers.last_login = datetime.now()
            globalUsers.save()
            save_login_log(request=request, status=True, msg=msg, user=globalUsers)
            # 缓存用户的jwt token
            if IS_SINGLE_TOKEN:
                redis_conn = get_redis_connection("singletoken")
                k = "lee-single-token{}".format(globalUsers.id)
                TOKEN_EXPIRE_CONFIG = getattr(settings, "SIMPLE_JWT", None)
                if TOKEN_EXPIRE_CONFIG:
                    TOKEN_EXPIRE = TOKEN_EXPIRE_CONFIG["ACCESS_TOKEN_LIFETIME"]
                    redis_conn.set(k, data["access"], TOKEN_EXPIRE)
            return DetailResponse(data=data, msg=msg)
        else:
            msg = "账号/密码错误"
            save_login_log(request=request, status=False, msg=msg, user=globalUsers)
            return ErrorResponse(msg=msg)


class GuestActivateView(CustomAPIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username", None)
        if not username or not isinstance(username, str) or len(username) < 3:
            return ErrorResponse(msg="username不合法")

        globalUsers = GlobalUsers.objects.filter(username=username).first()
        created_global = False
        if not globalUsers:
            globalUsers = GlobalUsers(username=username, is_active=True, is_guest=True, name=username)
            globalUsers.set_unusable_password()
            globalUsers.save()
            created_global = True

        from system.models import Users, Role

        role = Role.objects.filter(key="guest").first()
        if not role:
            role = Role.objects.create(name="游客", key="guest", sort=999, status=True)

        tenant_user = Users.objects.filter(username=username).first()
        if not tenant_user:
            name = f'游客{random.randint(1000, 9999)}'
            from system.models import Dept
            tenant_user = Users.objects.create(
                username=username,
                name=name,
                identity=1,
                is_active=True,
                dept_id= Dept.objects.filter(Q(parent__isnull=True) | Q(parent_id=0)).order_by("-sort").first().id,
            )
        tenant_user.role.add(role)
        tenant_user.save()

        from tenants.models import GlobalUserClientRelation

        client = getattr(request, "tenant", None)
        if client:
            relation = GlobalUserClientRelation.objects.filter(client=client, globalUsers=globalUsers).first()
            if not relation:
                relation = GlobalUserClientRelation.objects.create(
                    client=client,
                    globalUsers=globalUsers,
                    system_user_id=tenant_user.id,
                    is_active=True,
                    active_datetime=timezone.now(),
                )
            else:
                relation.system_user_id = tenant_user.id
                relation.is_active = True
                relation.active_datetime = timezone.now()
                relation.save()

        globalUsers.system_user_id = tenant_user.id
        globalUsers.save()

        data = LoginSerializer.get_token(globalUsers)
        return DetailResponse(data=data, msg="游客激活成功")


