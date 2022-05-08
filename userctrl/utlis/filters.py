"""
利用django自带的DRM查询和 第三方插件django_filters 组成过滤器
https://docs.djangoproject.com/zh-hans/3.2/ref/models/querysets/#field-lookups
djangodrm查询参数后缀:

lt:小于
gt:大于
lge:小于等于
gte:大于等于
exact:完全匹配
iexact:不区分大小写完全匹配
contains:
icontains:



"""
from django_filters import rest_framework as filter
from ..models import UserctrlApp


class AppFilter(filter.FilterSet):
    # 变量名 与 field_name 需要一致才生效
    app_name = filter.CharFilter(field_name='app_name', lookup_expr='contains')
    remark = filter.CharFilter(field_name='remark', lookup_expr='contains')

    class Meta:
        model = UserctrlApp
        fields = ['app_name']
