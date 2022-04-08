"""
数据校验中间件：
server_to_server: 服务端对服务端
"""

import time
import json
import base64
import redis
import rsa
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from rest_framework import status
from baseuser.utils.signature import sing_verify
from baseuser.redis_pool import REDIS_POOL
import re


class VerifyDataMiddleware:
    """
    数字签名：
    客户端发送的sign和前端发送的公钥验证数据完整性
    客户端端发送的都是经过base64编码的数据
    需要解码
    :param request:
    :return:
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        pass

    def server_to_server(self, request: HttpRequest):
        """
        服务端对服务端 交互数字签名验证
            1.验证RSA数字签名（数据完整性）
            2.验证nonce参数和时间戳（防重放）
        请求格式：
            querystr: /login/?t=&nonce=
            body:
            {
                email:'',
                password:aes_encry(password),
                secret_key: server_pk_encry(aes_key),
            }
            header：
            {
                'X-SIGN': client_priv_key_encry(hash(body))
                'X-KEY': client_pk
            }

            json 格式：
            值前面会有空格
            健值需要双引号
            {
                "email": "cxxrong@163.com",
                "password": "ZImpiDehWxMeSV543oULiw=="
            }


        :param request:
        :return:
        """
        if self.is_common_url(request.path):
            return self.get_response(request)
        x_sign = request.headers.get('X-SIGN')  # 数字签名
        x_pk = request.headers.get('X-KEY')  # 客户端公钥
        if not x_sign or not x_pk:
            return JsonResponse(data={"errcode": 40007,
                                      "errmsg": "header errors:'X-SIGN' and 'X-PK' "},
                                json_dumps_params={"ensure_ascii": False},
                                status=status.HTTP_400_BAD_REQUEST)
        # 数字签名解码部分
        client_sign = base64.b64decode(x_sign)
        client_pub_key = b'-----BEGIN RSA PUBLIC KEY-----\n' \
                         + x_pk.replace('\\n','\n').encode('utf-8') \
                         + b'\n-----END RSA PUBLIC KEY-----'

        client_pub_key = rsa.PublicKey.load_pkcs1(client_pub_key)
        data = None

        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body.decode("utf-8"))

        data['t'] = int(request.GET.get('t'))
        data['nonce'] = request.GET.get('nonce')

        if not request.GET.get('t') or not data['nonce']:
            response = JsonResponse(data={"errcode": 40004, "errmsg": "缺少查询参数时间戳t和nonce"},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)
            return response

        if sing_verify(data, client_pub_key, client_sign):
            if int(time.time()) - data['t'] > settings.TIMESTAMP_DELTA.seconds:
                # 时间戳判断是否过期
                response = JsonResponse(data={"errcode": 40005, "errmsg": "时间戳错误"},
                                        json_dumps_params={"ensure_ascii": False},
                                        status=status.HTTP_400_BAD_REQUEST)
                return response

            redis_client = redis.Redis(connection_pool=REDIS_POOL)
            result = redis_client.sadd("nonce", data['nonce'])
            if redis_client.scard("nonce") == 1:
                redis_client.expire("nonce", 24 * 3600)
            redis_client.close()

            if not data['nonce'] or result == 0:
                # 是否在缓存有
                # 缓存需要设置过期时间一般为一天
                # 要确保唯一性，最好使用record,但会增加数据压力
                response = JsonResponse(data={"errcode": 40006, "errmsg": "nonce错误"},
                                        json_dumps_params={"ensure_ascii": False},
                                        status=status.HTTP_400_BAD_REQUEST)
                return response
            # password = data.get('password')
            # aes_key = data.get('aes_key')
            # aes_key = rsa_decrypt(aes_key, settings.RSA_PRIVE_KEY)
            # clear_password = aes_decrypt(aes_key, password)
            # data['password'] = clear_password
            # request._body = json.dumps(data, ensure_ascii=False)
            response = self.get_response(request)

        else:
            response = JsonResponse(data={"errcode": 40000, "errmsg": "数据完整性校验失败"},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)
        return response

    def client_to_server(self, request: HttpRequest):
        """
        前端 对 服务端请求
        RSA + AES
        数字签名: AES(HASH(DATA)) RSA(AESKEY)
        请求数据:
        headers{
            "X-SIGN":"AES(HASH(DATA))",
            "X-KEY":"RSA(AESKEY)"
        }

        body{
            "DATA": {
                "USERNAME":"A",
                "PASSWORD":"AES(password)",

            }
        }
        :param request:
        :return:
        """

    def validate_base(self, request: HttpRequest):
        response = self.get_response(request)
        if self.is_common_url(request.path):
            return response

        data = None

        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body.decode("utf-8"))

        x_sign = request.headers.get('X-SIGN')
        x_key = request.headers.get('X-KEY')
        timestamps = data['t']
        nonce = data['nonce']

        # 1.判读是否有签名和验证KEY.fgh,/

        if not x_sign or not x_key:
            response = JsonResponse(data={"errcode": 40007,
                                          "errmsg": "header errors:'X-SIGN' and 'X-PK' "},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)

        # 2.时间戳和nonce是否存在
        if not timestamps or not nonce:
            response = JsonResponse(data={"errcode": 40004, "errmsg": "缺少查询参数时间戳t和nonce"},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)

        # 3.时间戳判断是否过期
        if int(time.time()) - data['t'] > settings.TIMESTAMP_DELTA.seconds:
            response = JsonResponse(data={"errcode": 40005, "errmsg": "时间戳错误"},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)

        # 4.nonce是否重复
        redis_client = redis.Redis(connection_pool=REDIS_POOL)
        result = redis_client.sadd("nonce", data['nonce'])
        if redis_client.scard("nonce") == 1:
            redis_client.expire("nonce", 24 * 3600)
        redis_client.close()

        if not data['nonce'] or result == 0:
            # 是否在缓存有
            # 缓存需要设置过期时间一般为一天
            # 要确保唯一性，最好使用record,但会增加数据压力
            response = JsonResponse(data={"errcode": 40006, "errmsg": "nonce错误"},
                                    json_dumps_params={"ensure_ascii": False},
                                    status=status.HTTP_400_BAD_REQUEST)

        return response

    @staticmethod
    def is_common_url(path):
        is_match = re.match(r'/api/common/.+', path)
        if not is_match:
            return False
        else:
            return True

