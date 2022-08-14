from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse

"""
自定义rest framework 返回的数据格式
1.原本错误的是应该在exception_handler处理，不知道为什么不成功了..（/login 401）
2.现在只能使用renderer处理

解决：
原因是restframework的设置没有被重新读取，至于为什么没有重新读取不清楚。。
settings.py:


rest_settings.DEFAULTS['EXCEPTION_HANDLER'] = 'baseuser.exception.custom_exception_handler'
rest_settings.DEFAULTS['DEFAULT_RENDERER_CLASSES'] = ['baseuser.render.CustomRenderer']

"""


class CustomRenderer(JSONRenderer):

    """
    正常情况: {'errmsg':'','errcode':0, 'data':...}  HTTP：200
    非正常情况：
        1.系统异常（如用户认证错误）{'errmsg':ErrorDetail, 'errcode': http_status}
        2.自定义的异常 {'errmsg':Exception.default_detail, 'errcode': Exception.default_code }

    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        print('customer render:', data)
        # print(accepted_media_type)
        # print(renderer_context)
        # response data 经过视图处理
        if renderer_context:

            errmsg = ''
            code = renderer_context['response'].status_code
            ret = {
                'errmsg': errmsg,
                'errcode': code,
                'http_status':renderer_context['response'].status_code
            }
            if code != 200:
                if data.get('detail') is not None:
                    # rest framework 系统返回
                    errmsg = data['detail']
                else:
                    # 自定义返回错误内容
                    errmsg = data['errmsg']
                    code = data['errcode']
            else:
                code = 0
                if data.get('errmsg'):
                    errmsg = data['errmsg']

            ret['errmsg'] = errmsg
            ret['errcode'] = code

            if ret['errcode'] == 0 and data.get('data') is not None:
                ret['data'] = data.get('data')
            # 自定义返回数据格式

            # 返回JSON数据
            return JsonResponse(ret, json_dumps_params={'ensure_ascii': False},
                                content_type='application/json,charset=utf-8')
        else:

            return super().render(data, accepted_media_type, renderer_context)