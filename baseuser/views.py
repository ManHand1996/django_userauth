"""
API:
    Login
    Logout
    Register
    VerifyEmail
    RSAPubKey
"""
import logging
from urllib import parse
from django.middleware.csrf import get_token
from django.http import HttpRequest,JsonResponse
from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from django.contrib import messages
from django.conf import settings

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status

from userauth.utils.render import CustomRenderer
from userauth.utils.exception import CustomException
from baseuser.utils.account_vervify import send_vervify_email, token_decode
from baseuser.utils.serializers import TokenSerializer
from baseuser.utils.decorators import validate_base
from baseuser.utils.encrys import FILE_ROOT_PATH

from mama_cas.models import ServiceTicket
from mama_cas.utils import redirect
from mama_cas.utils import to_bool
from django.contrib.auth import get_user_model, authenticate, login
User = get_user_model()

logger = logging.getLogger(__name__)
# Create your views here.


@validate_base
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
    """
    Login with JWT
    """
    renderer_classes = [CustomRenderer]
    serializer_class = TokenSerializer


class CASLogin(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request: Request):
        service = parse.unquote(request.GET.get('service'))
        renew = to_bool(request.GET.get('renew'))
        gateway = to_bool(request.GET.get('gateway'))

        if renew:
            logger.debug("Renew request received by credential requestor")
        elif gateway and service:
            logger.debug("Gateway request received by credential requestor")
            if request.user.is_authenticated:
                st = ServiceTicket.objects.create_ticket(service=service, user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service, 'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                return redirect(service)
        elif request.user.is_authenticated:
            if service:
                logger.debug("Service ticket request received by credential requestor")

                st = ServiceTicket.objects.create_ticket(service=service, user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service, 'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                msg = _("You are logged in as %s") % request.user
                messages.success(request, msg)
        logger.warning("Sasfasfasfas")
        return redirect(settings.CAS_LOGIN_URL, params={'service': service})

    def post(self, request: Request):
        print('CASLogin:', request)
        authenticate_kwargs = {
            User.USERNAME_FIELD: request.data[User.USERNAME_FIELD],
            'password': request.data['password'],
            'request': request
        }
        user = authenticate(**authenticate_kwargs)
        if not isinstance(user, User):
            raise CustomException('密码或邮箱错误', 50001,
                            status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        logger.warning("Single sign-on session started for %s" % user)

        # if form.cleaned_data.get('warn'):
        #     self.request.session['warn'] = True

        service = parse.unquote(request.GET.get('service'))

        if service:
            st = ServiceTicket.objects.create_ticket(service=service, user=user, primary=True)
            red = redirect(service, params={'ticket': st.ticket})
            red.headers.setdefault('Access-Control-Allow-Origin', 'http://127.0.0.1:8001')
            red.headers.setdefault('redirect', 'true')
            red.status_code = 401
            return red

        return redirect('cas_login')

    def warn_user(self):
        """
        Returns ``True`` if the ``warn`` parameter is set in the
        current session. Otherwise, returns ``False``.
        """
        return self.request.session.get('warn', False)


class Logout(APIView):
    """
    登出
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def post(self, request: Request):

        return Response({'email':request.user.email}, status.HTTP_200_OK)


class Register(APIView):
    """
    注册接口
    """
    renderer_classes = [CustomRenderer]

    @validate_base
    def post(self, request: Request):

        errcode, msg, user = self.validate(request.data)
        if errcode == 0:
            # 发送邮箱验证, 可以使用celery处理，或其他异步方式执行
            content_msg = "亲爱的用户:%s ,请点击以下连接完成邮箱验证" % user.username
            send_status = send_vervify_email('', '注册邮箱验证', [user.email],
                                             content_msg=content_msg,
                                             data={'type': 'register', 'user_id': user.id})
            if send_status == 0:
                return Response({'errcode': 0, 'errmsg': '注册成功，请查看邮箱完成验证'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'errcode': 0, 'errmsg': '注册成功，请查看邮箱完成验证'},
                                status=status.HTTP_200_OK)

        else:
            raise CustomException(msg, errcode)
            # return Response({'errcode': errcode, 'errmsg': msg}, status=status.HTTP_400_BAD_REQUEST)

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
            username = data.get('username')
            try:
                user = User.objects.get(email=email)
            except Exception as ex:
                print(ex)
                user = None
            else:
                pass
            if user is None:
                user = User(email=email)
                user.set_password(password)
                if username:
                    user.username = username
                user.is_active = False
                user.save()
            else:
                msg = '该邮箱已被注册'
                errcode = 30002
        else:
            msg = '邮箱和密码不能为空'
            errcode = 30001
        return (errcode, msg, user)


class RSAPubKey(APIView):
    """
    请求加密公钥
    """
    def get(self, request: Request):

        with open(FILE_ROOT_PATH.joinpath('public_key.pem'), 'rb') as f:
            pk_bytes = bytes(f.read())

            return Response({"data": pk_bytes.decode('utf-8')},
                            status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request: Request):
        token = request.query_params.get('token')
        if not token:
            raise CustomException('bad auth verify', 20001)
            # return Response({'errcode': 40009, 'errmsg': 'access token is none'},
            #                 status=status.HTTP_400_BAD_REQUEST)
        else:
            decode_token = token_decode(token)

            if not decode_token:
                raise CustomException('bad auth verify', 20002)
                # return Response({'errcode': 40010, 'errmsg': 'bad auth verify '},
                #                 status=status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.get(id=decode_token.get('user_id'))
                if user.is_active:
                    return Response({'errcode': 0, 'errmsg': '邮箱已验证'},
                                    status=status.HTTP_200_OK)
                user.is_active = True
                user.verify_date = localtime()
                user.save()
                return Response({'errcode': 0, 'errmsg': '邮箱验证成功'},
                                status=status.HTTP_200_OK)


class Test(APIView):
    def get(self, request, format=None):
        if not request.data.get('user'):
            raise CustomException()


class TestPage(APIView):

    renderer_classes = [CustomRenderer]

    def get(self, request:Request,format=None):

        return Response({'data':100})

    def post(self, request):
        # print(settings.REST_FRAMEWORK.get('EXCEPTION_HANDLER'))
        #return Response({'data': 100}, content_type='application/json')
        raise CustomException()


class CSRFToken(APIView):
    """
    CSRF TOKEN
    每个POST请求都需要在HTTP头部带上 X-CSRFToken
    """
    def get(self, request: Request):
        return Response({'data': get_token(request)}, status.HTTP_200_OK)


def http_404_handler(request: HttpRequest, exception):

    return JsonResponse({'errcode':status.HTTP_404_NOT_FOUND, 'errmsg':'页面不存在'},
                        content_type='application/json;',
                        json_dumps_params={'ensure_ascii':False}
                                , status=status.HTTP_404_NOT_FOUND)


