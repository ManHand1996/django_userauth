"""
自定义后端认证

配置：
settings.py: AUTHENTICATION_BACKENDS = []
"""
import base64

from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from baseuser.encrys import aes_decrypt, rsa_decrypt
from django.conf import settings
import json
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

    def authenticate(self, request: HttpRequest, email=None, password=None, **kwargs):
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
            # aes_key 解密密码
            data = json.loads(request.body.decode('utf-8'))
            secret_key = data['secret_key']
            password = data['password']
            aes_key = rsa_decrypt(secret_key, settings.RSA_PRIVE_KEY)
            decrypt_passwd = aes_decrypt(aes_key, password).decode('utf-8').strip()

            if auth_user.is_active and auth_user.check_password(decrypt_passwd):

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