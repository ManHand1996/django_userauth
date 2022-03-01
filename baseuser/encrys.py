'''

RSA

'''
import base64
import json

import rsa, string, random
from pathlib import Path
from Crypto.Cipher import AES
AES_LEN = 16

FILE_ROOT_PATH = BASE_DIR = Path(__file__).resolve().parent.parent
def rsa_gen():
    '''
    生成rsa 公钥私钥
    :return: 返回公钥给客户端
    '''
    # 返回RSA公钥
    pub_bytes, pri_bytes = None, None
    publickey, privekey = None, None
    with open(FILE_ROOT_PATH.joinpath('public_key.pem'), 'rb') as public:
        pub_bytes = bytes(public.read())

    with open(FILE_ROOT_PATH.joinpath('private_key.pem'), 'rb') as privete:
        pri_bytes = bytes(privete.read())

    if pub_bytes and pri_bytes:
        publickey = rsa.PublicKey.load_pkcs1(pub_bytes)
        privekey = rsa.PrivateKey.load_pkcs1(pri_bytes)

    if not publickey and not privekey:
        publickey, privekey = rsa.newkeys(512)
        with open(FILE_ROOT_PATH.joinpath('public_key.pem'), 'wb') as pub:
            pub.write(publickey.save_pkcs1())
        with open(FILE_ROOT_PATH.joinpath('private_key.pem'), 'wb') as pri:
            pri.write(privekey.save_pkcs1())
    return privekey,publickey
    # 保存私钥
    # seesionid ：{pubkey,privatekey}
    # print(publickey.save_pkcs1())
    # print(privekey.save_pkcs1())



def rsa_encrypt(sessionId, data, pub_key):
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
    key = randromchars(AES_LEN)
    mode = AES.MODE_CBC # 加密模式：加密块链
    init_str = randromchars(16) # 初始化向量
    aes_key = AES.new(key, mode, init_str).IV

    return aes_key


def aes_encrypt(aes_key, data):
    # print('加密前数据：', data)
    cipher = AES.AESCipher(aes_key)
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    if len(data) % AES_LEN != 0:
        data = data + bytes(b' ') * (AES_LEN - len(data) % AES_LEN)
    encrypt_data = cipher.encrypt(data)
    # print('AES 加密:', encrypt_data)
    return encrypt_data


def aes_decrypt(aes_key, data):
    cipher = AES.AESCipher(aes_key)
    if isinstance(data, str):
        data = base64.b64decode(data)
    elif isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    if len(data) % AES_LEN != 0:
        data = data + bytes(b' ') * (AES_LEN - len(data) % AES_LEN)
    decrpyt_data = cipher.decrypt(data)
    # print('AES 解密：', decrpyt_data)
    return decrpyt_data




if __name__ == '__main__':
    aes_key = aes_gen()

    encrypt_data = aes_encrypt(aes_key, 'manhand')
    print(aes_key)
    print(encrypt_data)
    # aes_decrypt(aes_key, encrypt_data)
    # publickey, privekey = rsa.newkeys(2048)
    # with open(FILE_ROOT_PATH.joinpath('jwt_public_key.pem'), 'wb') as pub:
    #     pub.write(publickey.save_pkcs1())
    # with open(FILE_ROOT_PATH.joinpath('jwt_private_key.pem'), 'wb') as pri:
    #     pri.write(privekey.save_pkcs1())
