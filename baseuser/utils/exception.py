from rest_framework.views import exception_handler, Response
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_403_FORBIDDEN


class CustomException(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = 'custom_default_detail'
    default_code = 40003

    def __init__(self, message, code, http_code=HTTP_403_FORBIDDEN):
        self.status_code = http_code
        self.default_code = code
        self.default_detail = message
        super(CustomException, self).__init__( message, code)


def custom_exception_handler(exc, context):
    print('custom_exception_handler:', exc)
    print('custom_exception_handler:', context.get("request").data)
    response = exception_handler(exc, context)
    response.content_type = 'application/json; charset=utf-8'
    # print('custom_exception:',response)
    # print('issubclass(CustomException)', )
    if isinstance(exc, CustomException):
        response = Response(data={'errcode': exc.get_codes(), 'errmsg': exc.detail}, status=exc.status_code,
                            content_type='application/json')
    elif issubclass(type(exc), APIException):
        # 自定义异常错误
        response = Response(data={'errcode': exc.default_code, 'errmsg': exc.default_detail}, status=exc.status_code,
                            content_type='application/json')
        # response.data['exception'] = 'h'
    else:
        # 系统异常错误
        response = Response(data=exc.get_full_details(), status=exc.status_code, content_type='application/json')
    return response


# def custom_exception_hanlder1(exc, context):
#     print('exec exception')
#     response = exception_handler(exc, context) if context else exception_handler(exc)
#
#     if response is not None and hasattr(response, "data"):
#         if hasattr(exc, "errno"):
#             response.data["errno"] = exc.errno
#         else:
#             response.data["errno"] = -1
#
#     return response
    # response = exception_handler(exc, context)
    # print('custom exception....')
    # if response is not None:
    #
    #     # response.data['errcode'] = response.status_code
    #     # response.data['errmsg'] = response.data['detail']
    #     response.data['hello'] = 'hahaha'
    #     # del response.data['detail']
    # else:
    #     response.data['exception'] = 'HHHH'
    # return response
