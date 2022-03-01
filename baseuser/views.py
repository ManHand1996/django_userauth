
# from django.contrib.auth.models import Group
import json

# from baseuser.models import User

from rest_framework import viewsets, permissions
from django.middleware.csrf import get_token
from baseuser.serializers import TokenSerializer
from django.http import HttpRequest,JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from baseuser.render import CustomRenderer
from baseuser.exception import CustomException
from baseuser.account_vervify import send_vervify_email, token_decode
# Create your views here.
from rest_framework import status

User = get_user_model()


def index(request: HttpRequest):
    # print(request.headers['X-CSRFToken'])
    if request.user.is_authenticated:
        result = {'errcode': 0, 'errmsg': ''}

    else:
        result = {'errcode': 401, 'errmsg': '用户未登陆'}
    # JSON 返回中文

    return JsonResponse(result, json_dumps_params={'ensure_ascii': False},
                        content_type='application/json,charset=utf-8')


class Login(TokenObtainPairView):
    renderer_classes = [CustomRenderer]
    serializer_class = TokenSerializer


class CSRFToken(APIView):
    """
    CSRF TOKEN
    每个POST请求都需要在HTTP头部带上 X-CSRFToken
    """
    def get(self, request: Request):
        return Response({'data':get_token(request)}, status.HTTP_200_OK)


class Logout(APIView):
    """
    登出
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def post(self, request: Request, format=None):

        return Response({'email':request.user.email}, status.HTTP_200_OK)


class Register(APIView):
    """
    注册接口
    """
    renderer_classes = [CustomRenderer]

    def post(self, request: Request):

        errcode, msg, user = self.validate(request.data)
        if errcode == 0:
            # 发送邮箱验证, 可以使用celery处理，或其他异步方式执行

            send_status = send_vervify_email('hahaha', '注册邮箱验证', ['1749460579@qq.com'], data={'type': 'register',
                                                                      'user_id': user.id})
            if send_status == 0:
                return Response({'errcode': errcode, 'errmsg': '注册成功，请查看邮箱完成验证'}, status=status.HTTP_200_OK)
            else:
                return Response({'errcode': errcode, 'errmsg': '注册成功，请查看邮箱完成验证'}, status=status.HTTP_200_OK)

        else:
            return Response({'errcode': errcode, 'errmsg': msg}, status=status.HTTP_200_OK)

    @staticmethod
    def validate(data):
        """

        :param data:
        :return: (is validated, response_msg)
        """
        # 邮箱
        # 密码
        errcode = 0
        msg = ''
        user = None
        if data.get('email') and data.get('password'):

            # 邮件认证
            email = data.get('email')
            password = data.get('email')
            username1 = data.get('username')
            try:
                user = User.objects.get(email=email)
            except Exception as e:
                user = None
            else:
                pass
            if user is None:
                user = User(email=email)
                user.set_password(password)
                if username1:
                    user.username = username1
                user.is_active = False
                user.save()
            else:
                msg = '该邮箱已被注册'
                errcode = 40002
        else:
            msg = '邮箱和密码不能为空'
            errcode = 40001
        return (errcode, msg, user)



class RSAPubKey(APIView):
    """
    请求加密公钥
    """
    def get(self, request: Request):
        return Response({"data": settings.RSA_PUB_KEY.save_pkcs1().decode()}, status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request: Request):
        token = request.query_params.get('token')
        if not token:
            return Response({'errcode': 40009, 'errmsg': 'access token is none'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            decode_token = token_decode(token)
            if not decode_token:
                return Response({'errcode': 40010, 'errmsg': 'bad auth verify '},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.get(id=decode_token.get('user_id'))
                user.is_active = True
                user.save()
                return Response({'errcode': 0, 'errmsg': '邮箱验证成功'},
                                status=status.HTTP_200_OK)


# class CustomException(APIException):
#     status_code = 405
#     default_detail = 'DDDDDDDD'
#     default_code = '自定义异常错误'



class Test(APIView):
    def get(self, request, format=None):
        if not request.data.get('user'):
            raise CustomException()



class TestPage(APIView):

    renderer_classes = [CustomRenderer]

    def get(self, request,format=None):
        return Response({'data':100})

    def post(self, request):
        from rest_framework.settings import settings
        # print(settings.REST_FRAMEWORK.get('EXCEPTION_HANDLER'))
        #return Response({'data': 100}, content_type='application/json')
        raise CustomException()




def http_404_handler(request: HttpRequest, exception):

    return JsonResponse({'errcode':status.HTTP_404_NOT_FOUND, 'errmsg':'页面不存在'},
                        content_type='application/json;',
                        json_dumps_params={'ensure_ascii':False}
                                , status=status.HTTP_404_NOT_FOUND)
