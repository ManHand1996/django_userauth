'''

RSA

'''

__all__ = ['FILE_ROOT_PATH', 'rsa_gen_openssl', 'aes_decrypt', 'rsa_decrypt', 'data_hash']
import os
import re
import base64
import json
import rsa
import string
import random
import subprocess
import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from binascii import b2a_base64, a2b_base64
AES_LEN = 32
RSA_LEN = 1024
FILE_ROOT_PATH = BASE_DIR = Path(__file__).resolve().parent.parent.parent
REMOVE_BYTES = ['\x01', '\x02', '\x03', '\x04',
                '\x05', '\x06', '\x07', '\x08',
                '\x09', '\x0a', '\x0b', '\x0c',
                '\x0d', '\x0e', '\x0f', '\x10',
                ]

def rsa_gen_openssl(use_openssl=False):
    """

    :param use_openssl: 是否使用OPENSSL 生成RSA 密钥对
    :return:
    """
    # 返回RSA公钥
    pub_bytes, pri_bytes = None, None
    publickey, privekey = None, None
    pubkey_path = FILE_ROOT_PATH.joinpath('public_key.pem')
    prikey_path = FILE_ROOT_PATH.joinpath('private_key.pem')
    if not os.path.exists(pubkey_path) or not os.path.exists(prikey_path):
        subprocess.run(["touch", prikey_path])
        subprocess.run(["touch", pubkey_path])
        if use_openssl:
            gen_cml = "openssl genrsa -out %s 1024" % prikey_path
            save_cml = "openssl rsa -pubout -in %s -out %s" % (prikey_path,
                                                               pubkey_path)
            subprocess.run([gen_cml], shell=True, check=True, capture_output=True)
            subprocess.run([save_cml], shell=True, check=True, capture_output=True)

    with open(pubkey_path, 'rb') as public:
        pub_bytes = bytes(public.read())

    with open(prikey_path, 'rb') as privete:
        pri_bytes = bytes(privete.read())

    publickey = rsa.PublicKey.load_pkcs1_openssl_pem(pub_bytes)
    privekey = rsa.PrivateKey.load_pkcs1(pri_bytes)

    return privekey, publickey
    # 保存私钥
    # seesionid ：{pubkey,privatekey}
    # print(publickey.save_pkcs1())
    # print(privekey.save_pkcs1())


def rsa_encrypt(data, pub_key):
    # 确认客户端 -- sessionId
    encrypt_data = data
    if isinstance(data, str):
        encrypt_data = data.encode('utf-8')
    elif isinstance(data, dict):
        encrypt_data = json.dumps(data).encode('utf-8')
    return rsa.encrypt(encrypt_data, pub_key)


def rsa_decrypt(data, pri_key):
    decrypt_data = data
    if isinstance(data, dict):
        decrypt_data = json.dumps(data).encode('utf-8')
    elif isinstance(data, str):
        decrypt_data = base64.b64decode(data)
        # decrypt_data = b2a_base64(data)
    return rsa.decrypt(decrypt_data, pri_key)


'''
AES 256
'''


def aes_gen():
    #
    def randromchars(len):
        charts_set = string.ascii_letters + string.digits
        return ''.join(random.sample(charts_set, len))

    # 对称密钥: 16bytes(AES-128) 24bytes(AES-192) 32bytes(AES-256)
    key = bytes(randromchars(AES_LEN))
    mode = AES.MODE_CBC  # 加密模式：加密块链
    iv = os.urandom(16)  # 偏移量

    # aes_key = AES.new(key=key, mode=mode, IV=iv).IV

    return key, iv


def aes_encrypt(aes_key: bytes, iv:bytes, data: bytes):

    cipher = AES.new(key=aes_key, mode=AES.MODE_CBC, IV=iv)
    data = aes_pkcs7_pad(data)
    print(data)
    encrypt_data = cipher.encrypt(data)

    return encrypt_data


def aes_decrypt(aes_key: bytes, iv: bytes, data):
    cipher = AES.new(key=aes_key, mode=AES.MODE_CBC, IV=iv)
    decrpyt_data = cipher.decrypt(a2b_base64(data))

    # 去除 填充字符 chr(1) - chr(16)
    for i in REMOVE_BYTES:
        decrpyt_data = decrpyt_data.strip(i.encode())
    return decrpyt_data


def aes_pkcs7_pad(data):
    """
    填充方式:pcsk#7标准
    :param data:
    :return:
    """
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def pkcs7_unpadding(padded_data):
    pass
    # unpadder = padding.PKCS7(64).unpadder()
    # data = unpadder.update(padded_data)
    #
    # try:
    #     uppadded_data = data + unpadder.finalize()
    # except ValueError:
    #     raise Exception('无效的加密信息!')
    # else:
    #     return uppadded_data


def data_hash(data: dict):
    """
    对数据进行顺序排序然后使用SHA256 计算摘要
    :param data: dict
    :return: base64.encode(hex)
    """
    sha_hash = hashlib.sha256()
    sorted_data = dict(sorted(data.items(), key=lambda x: x[0]))
    data_str = json.dumps(sorted_data).encode()
    print(data_str)
    sha_hash.update(data_str)
    return sha_hash.hexdigest()

# def aes_pkcs7_unpad(data):
#     unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
#     uppad_data = unpadder.update(data)
#     try:
#         uppad_data += unpadder.finalize()
#     except ValueError:
#         return bytes('')
#     else:
#         return uppad_data



if __name__ == '__main__':
    # key = 'TNTPR8ZzTJhN66BLPJUzzasoFAyQVAtQ'
    # iv = key[:16]
    #
    # data = 'YllQWOplzrc8gr6v5Y1Unw=='
    # # encrypt_data = base64.b64decode(data)
    # decrypt_data = aes_decrypt(key.encode(), iv.encode(), data)
    # print(a2b_base64(decrypt_data))

    rsa_gen_openssl(True)
    print(Path(__file__).resolve().parent.parent)

