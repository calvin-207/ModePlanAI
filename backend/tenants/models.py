from django.db import models
from utils.models import CoreModel,BaseModel
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import AbstractBaseUser, UserManager

class Client(BaseModel, TenantMixin):
    code = models.CharField(max_length=100, unique=True, verbose_name="客户编码")
    name = models.CharField(max_length=100, verbose_name="客户名称")

    paid_until =  models.DateField(verbose_name="付费截止日期", blank=True, null=True)

   
    on_trial = models.BooleanField(verbose_name="是否在试用期", default=True)
    trial_end = models.DateField(verbose_name="试用期结束日期", blank=True, null=True)

    auto_create_schema = True

class Domain(DomainMixin):
    pass


class GlobalUsers(AbstractBaseUser, BaseModel):

    GENDER_CHOICES = (
        (0, "未知"),
        (1, "女"),
        (2, "男"),
    )

    IDENTITY_CHOICES = (
        (0, "超级管理员"),
        (1, "系统管理员"),
        (2, "前端用户"),
    )
    username = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='用户账号', help_text="用户账号")
    email = models.EmailField(max_length=60, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=30,verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=200,verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    nickname = models.CharField(max_length=100, help_text="用户昵称", verbose_name="用户昵称",default="", null=True, blank=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, verbose_name="性别", null=True, blank=True, help_text="性别",default=0)
    
    login_error_nums = models.IntegerField(default=0, verbose_name="登录错误次数", help_text="登录错误次数")
    identity = models.SmallIntegerField(choices=IDENTITY_CHOICES, verbose_name="身份标识", null=True, blank=True, default=2,help_text="身份标识")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='钱包余额')
    is_active = models.BooleanField(verbose_name="状态",default=True)
    is_staff = models.BooleanField(verbose_name="是否员工",default=False)
    is_superuser = models.BooleanField(verbose_name="是否超级管理员", default=False)
    # 是否是游客模式
    is_guest = models.BooleanField(verbose_name="是否游客模式", default=False)

    objects = UserManager()
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "glboal_users"
        verbose_name = '全局用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class LoginLog(CoreModel):
    LOGIN_TYPE_CHOICES = (
        (1, '后台登录'),
    )
    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名")
    ip = models.CharField(max_length=32, verbose_name="登录ip", null=True, blank=True, help_text="登录ip")
    agent = models.CharField(max_length=1500,verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=150, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    login_type = models.IntegerField(default=1, choices=LOGIN_TYPE_CHOICES, verbose_name="登录类型", help_text="登录类型")
    ip_area = models.CharField(max_length=100, verbose_name="IP归属地", null=True, blank=True, help_text="IP归属地")
    msg = models.CharField(max_length=255,verbose_name="自定义内容", null=True, blank=True)
    status = models.BooleanField(default=True, verbose_name="响应状态", help_text="响应状态")

    class Meta:
        db_table = 'login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
