import redis
import rsa
import time
from django.http import HttpRequest, JsonResponse
from baseuser.signature import sing_verify
from baseuser.encrys import rsa_decrypt, aes_decrypt
from django.conf import settings
from rest_framework import status

import json
import base64
from baseuser.redis_pool import REDIS_POOL

"""
querystr: /login/?t=&nonce=
body:
{
	email:'',
	password:aes_encry(password),
	
	
	secret_key: server_pk_encry(aes_key),
}
header：{
	'X-SIGN': client_priv_key_encry(hash(body))
	'X-PK': client_pk
}

json 格式：
值前面会有空格
健值需要双引号
{
    "email": "cxxrong@163.com",
    "password": "ZImpiDehWxMeSV543oULiw=="
}

"""


class VerifyDataMiddleware():

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request:HttpRequest):

        """

        数字签名：
        前端发送的sign和前端发送的公钥验证数据完整性
        前端发送的都是经过base64编码的数据
        需要解码
        :param request:
        :return:
        """
        x_sign = request.headers.get('X-SIGN')
        x_pk = request.headers.get('X-PK')
        if not x_sign or not x_pk:
            return JsonResponse(data={"errcode": 40007, "errmsg":"header errors:'X-SIGN' and 'X-PK' "},
                                    json_dumps_params={"ensure_ascii":False},status=status.HTTP_400_BAD_REQUEST)
        # 数字签名部分
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
                         json_dumps_params={"ensure_ascii": False}, status=status.HTTP_400_BAD_REQUEST)
            return response

        if sing_verify(data, client_pub_key, client_sign):
            if int(time.time()) - data['t'] > settings.TIMESTAMP_DELTA.seconds:
                # 时间戳判断是否过期
                response = JsonResponse(data={"errcode": 40005, "errmsg": "时间戳错误"},
                                        json_dumps_params={"ensure_ascii": False}, status=status.HTTP_400_BAD_REQUEST)
                return response

            r = redis.Redis(connection_pool=REDIS_POOL)
            result = r.sadd("nonce", data['nonce'])
            if r.scard("nonce") == 1:
                r.expire("nonce", 24 * 3600)
            r.close()

            if not data['nonce'] or result == 0:
                # 是否在缓存有
                # 缓存需要设置过期时间一般为一天
                # 要确保唯一性，最好使用record,但会增加数据压力
                response = JsonResponse(data={"errcode": 40006, "errmsg": "nonce错误"},
                                        json_dumps_params={"ensure_ascii": False}, status=status.HTTP_400_BAD_REQUEST)
                return response
            # password = data.get('password')
            # aes_key = data.get('aes_key')
            # aes_key = rsa_decrypt(aes_key, settings.RSA_PRIVE_KEY)
            # clear_password = aes_decrypt(aes_key, password)
            # data['password'] = clear_password
            # request._body = json.dumps(data, ensure_ascii=False)
            response = self.get_response(request)

        else:
            response = JsonResponse(data={"errcode": 40000, "errmsg":"数据完整性校验失败"},
                                    json_dumps_params={"ensure_ascii":False},status=status.HTTP_400_BAD_REQUEST)
        return response

