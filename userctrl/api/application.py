"""
app 管理
appid 与 secret 分配

"""
import rest_framework.exceptions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import LimitOffsetPagination
from userauth.utils.render import CustomRenderer
from userauth.utils.exception import CustomException
from collections import OrderedDict
from ..utlis import (generators, restpermission, serializer, filters, common)
from ..models import UserctrlApp


class ApplicationViewSet(viewsets.ModelViewSet, common.CommonPagi):
    """
    对app这个实体进行 增删改查
    获取所有list, 查询集合,  分页等..
    """
    # queryset = UserctrlApp.objects.all()
    serializer_class = serializer.AppSerializer
    # permission_classes = [restpermission.ControlManagerPermission]
    permission_classes = []
    renderer_classes = [CustomRenderer]
    authentication_classes = []
    pagination_class = LimitOffsetPagination
    filterset_class = filters.AppFilter

    def get_object(self, pk=None):
        """
        单个实体对象查询
        :return:
        :rtype:
        """
        try:
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        except Exception as exp:
            raise rest_framework.exceptions.NotFound()
        return obj

    def get_queryset(self):
        return UserctrlApp.objects.all()

    # def filter_queryset(self, queryset):
    #     """
    #     排序, 分页, 搜索
    #     order:  ?order=id:desc
    #     paginatiuon: limit=20&offset=10
    #     search: keyword=
    #     """
    #     qs = super().filter_queryset(queryset)
    #     if self.request.query_params['limit'] and self.request.query_params['offset']:
    #         qs = self.paginate_queryset(qs)
    #
    #     return qs

    def list(self, request, *args, **kwargs):

        qs = self.filter_queryset(self.get_queryset())

        return Response({'data': self.get_paginated_data(qs, self)})

    def create(self, request, *args, **kwargs):
        """
        POST
        无确认对象, 执行多次结果可能不同,
        创建一个新的app, 根据id判断是否已经创建过.
        """
        result = {'data': {}}
        app_serializer = self.get_serializer(data=request.data)
        if app_serializer.is_valid():
            app_serializer.save()
            result['data'] = app_serializer.data
        else:
            result['data'] = app_serializer.errors

        return Response(result)

    def update(self, request, *args, **kwargs):
        """
        PUT 必须有确认对象参与
        无论执行多少次结果都不会变
        """
        app_obj = self.get_object(pk=kwargs.get('pk'))
        app_serializer = self.get_serializer(app_obj, data=request.data, partial=True)
        if app_serializer.is_valid():
            app_serializer.save()

        return Response({'data': app_serializer.data})

    def retrieve(self, request, *args, **kwargs):
        app_serializer = self.get_serializer(self.get_object(pk=kwargs.get('pk')))
        return Response({'data': app_serializer.data})

    def destroy(self, request, *args, **kwargs):
        app_obj = self.get_object(pk=kwargs.get('pk'))

        app_serializer = self.get_serializer(app_obj)
        app_serializer.destroy()
        return Response({'data': 'destroy application!'})


class GenerateApplication(APIView):
    renderer_classes = [CustomRenderer]
    # authentication_classes = [SessionAuthentication]
    permission_classes = [restpermission.ControlManagerPermission]

    def get(self):
        """

        :return: 返回临时 appid 与 secret
        :rtype:
        """
        data = {
            'app_id': generators.generate_appid(),
            'secret': generators.generate_secret()
        }

        if not (UserctrlApp.objects.get(app_id=data['app_id'])):
            data = {
                'app_id': generators.generate_appid(),
                'secret': generators.generate_secret()
            }

        return Response({'errcode': 0, 'errmsg': '', 'data': data},
                        status=status.HTTP_200_OK)


