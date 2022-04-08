"""
数据验证装饰器
验证:
1.判读是否有签名和验证KEY
2.时间戳和nonce是否存在
3.时间戳判断是否过期
4.nonce是否重复
5.数字签名验证:
    RSA + AES
        数字签名:HASH: SHA256  AES(HASH(DATA)) RSA(AESKEY)
        请求数据:
        headers{
            "X-SIGN":"AES(HASH(DATA))",
            "X-KEY":"RSA(AESKEY)"
        }

        body{

            "USERNAME":"A",
            "PASSWORD":"AES(password)",

        }
"""
import base64
import json
import time
import redis
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView as restAPIView
from rest_framework.request import Request as restRequest
from baseuser.redis_pool import REDIS_POOL
from baseuser.utils.exception import CustomException

from baseuser.utils.encrys import aes_decrypt, rsa_decrypt, data_hash


def validate_base(func):
    """

    :param func: 视图函数
    :return:
    """

    def wrapper(*args, **kwargs):
        is_authbackend = False
        request = args[0]  # WSGIRequest
        print('wrapper:', args)
        print('wrapper:', kwargs)
        if isinstance(request, restAPIView):
            # restfulAPIView
            request = args[1]

        if func.__name__ == 'authenticate':
            # custom auth backend request
            is_authbackend = True
            request = args[1]  # RESTFul API rest_framework.request.Request

        is_rest_request = isinstance(request, restRequest)

        data = None
        if request.headers.get('Content-Type') == 'application/json':
            if is_rest_request:
                data = request.data
            else:
                data = json.loads(request.body.decode('utf-8'))

        x_sign = request.headers.get('X-SIGN')
        x_key = request.headers.get('X-KEY')
        timestamps = data.get('t')
        nonce = data.get('nonce')

        # 1.判读是否有签名和验证KEY

        if not x_sign or not x_key:
            return response_or_exception(is_authbackend, {"errcode": 40001,
                                                          "errmsg": "header errors:'X-SIGN' and 'X-KEY' "},
                                         status.HTTP_400_BAD_REQUEST)

        # 2.时间戳和nonce是否存在
        if not timestamps or not nonce:
            return response_or_exception(is_authbackend, {"errcode": 40002, "errmsg": "缺少查询参数时间戳t和nonce"},
                                         status.HTTP_400_BAD_REQUEST)

        # 3.时间戳判断是否过期
        if int(time.time()) - timestamps > settings.TIMESTAMP_DELTA.seconds:
            return response_or_exception(is_authbackend, {"errcode": 40003, "errmsg": "时间戳错误"},
                                         status.HTTP_400_BAD_REQUEST)

        # 4.nonce是否重复
        redis_client = redis.Redis(connection_pool=REDIS_POOL)
        result = redis_client.sadd("nonce", nonce)
        if redis_client.scard("nonce") == 1:
            redis_client.expire("nonce", 24 * 3600)
        redis_client.close()

        if not data['nonce'] or result == 0:
            # 是否在缓存有
            # 缓存需要设置过期时间一般为一天
            # 要确保唯一性，最好使用record,但会增加数据压力
            return response_or_exception(is_authbackend, {"errcode": 40004, "errmsg": "nonce错误"},
                                         status.HTTP_400_BAD_REQUEST)

        # 5.数字签名验证
        encry_sign = x_sign.encode()
        aes_key = rsa_decrypt(x_key, settings.RSA_PRIVE_KEY).decode()
        iv = aes_key[::-1]
        decry_sign = aes_decrypt(aes_key.encode(), iv.encode(), encry_sign)
        decry_sign = base64.b64decode(decry_sign).hex()
        compute_sign = data_hash(data)

        if not compute_sign == decry_sign:
            return response_or_exception(is_authbackend, {"errcode": 40005, "errmsg": "签名错误"},
                                         status.HTTP_400_BAD_REQUEST)
        if is_authbackend:
            return func(args[0], request, email=kwargs.get('email'), password=kwargs.get('password'))
        else:
            return func(args[0], request)

    return wrapper


def response_or_exception(is_authbackend: bool, data: dict, http_status: int):
    """

    :param is_authbackend:
    :param data:
    :param http_status:
    :return:
    """
    if is_authbackend:
        exc = CustomException(data.get("errmsg"), data.get("errcode"))
        exc.status_code = http_status
        raise exc
    else:
        return JsonResponse(data=data,
                            json_dumps_params={"ensure_ascii": False},
                            status=http_status)



