"""
自定义后端认证

配置：
settings.py: AUTHENTICATION_BACKENDS = []
"""
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import get_user_model

UserModel = get_user_model()

# 验证后端， 密文传输。
# password加密：
# 数字签名

class CustomAuthBackend(BaseBackend):
    """
    用户名/邮箱 登陆验证
    """
    def get_user(self, user_id):
        return UserModel.objects.get(pk=user_id)

    def authenticate(self, request, email=None, password=None, **kwargs):
        print('CustomAuthBackend: start')
        # **kwargs 表单提交名称没有对应参数，则在此显示。
        # django-admin 后台登陆页面默认使用username作为用户名input标签
        if email is None:
            email = kwargs.get('username')
        try:
            auth_user = UserModel.objects.get(email=email)

        except ObjectDoesNotExist as e:

            return None
        else:

            if auth_user.is_active and auth_user.check_password(password):

                return auth_user
            return None


class TokenAuthBackend(BaseBackend):
    """
    TOKEN 身份验证
    """
    def get_user(self, user_id):
        return UserModel.objects.get(id=user_id)

    def authenticate(self, request:HttpRequest, token=None, **kwargs):
        request.headers.get('Authorization')