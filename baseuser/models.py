
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser , PermissionsMixin,UnicodeUsernameValidator,BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib.auth import authenticate, login


class CustomManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('请添加邮箱')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)

    def create_superuser(self, email, password=None):
        user = self.model(
            email=self.normalize_email(email),
            is_staff=True,
            is_superuser=True
        )
        user.set_password(password)
        user.save(using=self._db)



class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型：
    1.后端认证
    2.权限
    3.后台admin
    """
    username = models.CharField(verbose_name='用户名', max_length=30, validators=[UnicodeUsernameValidator()])
    email = models.EmailField(verbose_name='验证邮箱', unique=True)
    password = models.CharField(verbose_name='密码', max_length=256)
    phone_number = models.CharField(verbose_name='手机号码', max_length=11, default='')
    register_date = models.DateTimeField(verbose_name='注册时间', auto_now=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomManager()