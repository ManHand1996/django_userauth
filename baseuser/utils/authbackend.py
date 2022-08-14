"""
自定义后端认证

配置：
settings.py: AUTHENTICATION_BACKENDS = []
"""
import json
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import get_user_model, hashers
from django.conf import settings
from baseuser.utils.encrys import aes_decrypt, rsa_decrypt
from baseuser.utils.decorators import validate_base
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

    @validate_base
    def authenticate(self, request, email=None, password=None, **kwargs):

        # **kwargs 表单提交名称没有对应参数，则在此显示。
        # django-admin 后台登陆页面默认使用username作为用户名input标签
        print('authenticate:', request)
        print('authenticate:', self)
        if email is None:
            email = kwargs.get('username')
        try:
            auth_user = UserModel.objects.get(email=email)

        except ObjectDoesNotExist as e:
            return None
        else:
            # aes_key 解密密码
            if isinstance(request, HttpRequest):
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.data
            aes_key = request.headers.get('X-KEY')
            password = data['password']
            aes_key = rsa_decrypt(aes_key, settings.RSA_PRIVE_KEY).decode()
            iv = aes_key[::-1]
            decrypt_passwd = aes_decrypt(aes_key.encode(), iv.encode(), password).decode().strip()

            if auth_user.is_active and hashers.check_password(decrypt_passwd, auth_user.password):
                print('authbackend:', auth_user)
                return auth_user
            return None


class TokenAuthBackend(BaseBackend):
    """
    TOKEN 身份验证
    """
    def get_user(self, user_id):
        return UserModel.objects.get(id=user_id)

    def authenticate(self, request: HttpRequest, token=None, **kwargs):
        request.headers.get('Authorization')
