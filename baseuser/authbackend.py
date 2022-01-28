"""
自定义后端认证

配置：
settings.py: AUTHENTICATION_BACKENDS = []
"""
from django.contrib.auth.backends import BaseBackend

from baseuser.models import User

class UsernameAuthBackend(BaseBackend):

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, request, username=None, password=None):



class EmailAuthBackend(BaseBackend):

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, request, email=None, password=None):