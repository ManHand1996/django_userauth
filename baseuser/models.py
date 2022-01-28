
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    """
    自定义用户模型：
    1.后端认证
    2.权限
    3.后台admin
    """
    username = models.CharField(verbose_name='登陆名', max_length=30, unique=True)
    email = models.EmailField(verbose_name='验证邮箱', unique=True)
    password = models.CharField(verbose_name='密码', max_length=256)
    phone_number = models.CharField(verbose_name='手机号码', max_length=11, default='')
    register_date = models.DateTimeField(verbose_name='注册时间', auto_now=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'


