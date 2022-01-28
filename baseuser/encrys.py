'''

RSA

'''
import rsa, string, random
from Crypto.Cipher import AES
AES_LEN = 16
def rsa_gen():
    '''
    生成rsa 公钥私钥
    :return: 返回公钥给客户端
    '''
    # 返回RSA公钥
    publickey, privekey = rsa.newkeys(512)
    # 保存私钥
    # seesionid ：{pubkey,privatekey}

    return publickey


def rsa_encrypt(sessionId, data, pub_key):
    # 确认客户端 -- sessionId
    encrypt_data = data
    if not isinstance(data, bytes):
        encrypt = data.encode('utf-8')
    return rsa.encrypt(encrypt_data, pub_key)


def rsa_decrypt(data, pri_key):
    decrypt_data = data
    if not isinstance(data, bytes):
        decrypt_data = data.encode('utf-8')
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
    print('加密前数据：', data)
    cipher = AES.AESCipher(aes_key)
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    if len(data) % AES_LEN != 0:
        data = data + bytes(b' ') * (AES_LEN - len(data) % AES_LEN)
    encrypt_data = cipher.encrypt(data)
    print('AES 加密:', encrypt_data)
    return encrypt_data


def aes_decrypt(aes_key, data):
    cipher = AES.AESCipher(aes_key)
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    if len(data) % AES_LEN != 0:
        data = data + bytes(b' ') * (AES_LEN - len(data) % AES_LEN)
    decrpyt_data = cipher.decrypt(data)
    print('AES 解密：', decrpyt_data)
    return decrpyt_data




if __name__ == '__main__':
    aes_key = aes_gen()
    encrypt_data = aes_encrypt(aes_key, 'I have a trouble problem!')
    aes_decrypt(aes_key, encrypt_data)
