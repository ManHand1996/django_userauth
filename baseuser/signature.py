"""
signature：
对数据进行签名验证
HASH
SIGN

约定hash算法 SHA-1
约定公钥
"""
import rsa

HASH_METHOD = 'SHA-1'

def sign_sign(data, pri_key):
    """

    :param data: 需要签名的数据 bytes
    :param pri_key: 私钥
    :return: 数字签名
    """
    if not isinstance(data):
        data = data.encode('utf-8')
    return rsa.sign(data, pri_key, HASH_METHOD)


def sing_verify(data, pub_key, signature):

    """
    :param data: 验证的数据
    :param pub_key: 公钥
    :param signature:
    :return:
    """
    if not isinstance(data):
        data = data.encode('utf-8')
    try:
        hash_name = rsa.verify(data, signature, pub_key)
        if hash_name == HASH_METHOD:
            return True
        else:
            return False
    except Exception as error:
        return False