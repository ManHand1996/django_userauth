"""
appid and secret generate
"""

import secrets
import string


def generate_appid(length=40):
    rand = secrets.SystemRandom()
    charset = string.ascii_letters + string.digits
    return ''.join(rand.choice(charset) for x in range(length))


def generate_secret(length=30):
    return secrets.token_urlsafe(length)


if __name__ == '__main__':
    app_id = generate_appid()
    secret = generate_secret()
    print('appid:', app_id)
    print('secret:', secret)
