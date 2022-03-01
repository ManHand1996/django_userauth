import datetime
import time
import datetime
import jwt
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.template import loader
from userauth import settings as usettings
# User = get_user_model()


def send_vervify_email(email_body, email_title, receive_emails, content_msg, data):
    """
    发送邮件认证：注册邮件认证或修改密码邮件认证
    :param email_body:
    :param email_title:
    :param receive_emails:
    :return:
    """
    vervify_link = settings.DOMAIN + '/vervify?token=' + token_encode(data)
    html_msg = loader.get_template(
        'vervifyemail_template.html',
        {
            'content_msg': content_msg,
            'verify_link': vervify_link
        }

    )
    send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, receive_emails, html_message=html_msg)
    return send_status


def token_encode(data: dict):
    """
    custom jwt using rsa
    :return:

    exp：过期时间
    nbf: 在该时间前不能处理
    iss: jwt颁发者，解密时需要提供
    aud：jwt受众，解密时需要提供
    iat：jwt颁发时间
    """
    now_timestamp = int(time.time())
    if isinstance(data, dict):
        data.update({'exp': now_timestamp + datetime.timedelta(minutes=5).seconds,
                     'iat': now_timestamp})

    jwt_token = jwt.encode(data, settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithm="RS256")
    return jwt_token


def token_decode(jwt_token):
    try:
        decode = jwt.decode(jwt_token, settings.SIMPLE_JWT.get('VERIFYING_KEY'), algorithms=["RS256"])
    except jwt.ExpiredSignatureError:
        return None
    else:
        return decode


if __name__ == '__main__':
    settings.configure(default_settings=usettings)
    token = token_encode({'user_id': 1})
    print(token)
    decode_token = token_decode(token)
    print(decode_token)