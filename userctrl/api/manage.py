"""

"""

import uuid
import rest_framework.exceptions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.shortcuts import get_object_or_404

from userctrl.utlis import serializer
from userctrl import models
from userauth.utils.render import CustomRenderer
from userauth.utils.exception import CustomException
from userctrl.utlis.common import CommonPagi


class ResourceViewSet(ModelViewSet, CommonPagi):
    """
    各类资源CURD接口
    url:
     /resource/menu/
     /resource/element/
     /resource/file/
     /resource/data/
    新增资源类型,修改 models属性 {
        'part of url': django.models
    }
    """
    authentication_classes = []
    pagination_class = LimitOffsetPagination
    permission_classes = []
    renderer_classes = [CustomRenderer]
    serializer_class = serializer.ResourceSerializer
    model_name = None
    models = {
        'menu': models.UserctrlResrcmenu,
        'data': models.UserctrlResrcdata,
        'file': models.UserctrlResrcfile,
        'element': models.UserctrlResrcelement
    }

    def set_models(self):
        """
        根据url动态获取model: /resrc/menu/
        :return:
        :rtype:
        """
        url = self.request.build_absolute_uri()
        model_choose = list(filter(lambda x: x in url, self.models.keys()))
        self.model_name = self.models[model_choose.pop()]

    def get_serializer_class(self):
        """
        重写 get_sserializer_class ,动态设置serialzer的meta.model
        :return:
        :rtype:
        """
        if self.model_name is None:
            self.set_models()
        self.serializer_class.Meta.model = self.model_name
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):

        return super(ResourceViewSet, self).get_serializer(*args, **kwargs)

    def get_object(self, pk=None):
        try:
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        except Exception as exp:
            raise rest_framework.exceptions.NotFound(detail='对象没有找到')
        return obj

    def get_queryset(self):
        if self.model_name is None:
            self.set_models()
        return self.model_name.objects.all()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        return Response({'data': self.get_paginated_data(qs, self)})

    def create(self, request, *args, **kwargs):
        """
        资源添加前端需要提交:
        资源名称
        资源类型
        所属app
        对应类型的资源信息:{}
        resrc_code =  resrc_type +
        request.data = {
            'resrc_name':'',
            'resrc_type_id':'',
            'resrc_code'
            'app_id':'',
            'info':{}
        }
        """
        result = {'data': {}}
        new_resrc = models.UserctrlResrc.objects.create(
            resrc_name=request.data.get('resrc_name'),
            resrc_code=uuid.uuid4().hex,
            app_id=request.data.get('app_id'),
            resrc_type_id=request.data.get('resrc_type_id')

        )

        resrc_detail = request.data.get('info')
        # serializer 的外健引用值(id) 不需要添加_id, 与django的model一样
        resrc_detail['resrc'] = new_resrc.id
        obj_serializer = self.get_serializer(data=resrc_detail)
        if obj_serializer.is_valid(raise_exception=True):
            obj_serializer.save()
            result['data'] = obj_serializer.data
        return Response(result)

    def update(self, request, *args, **kwargs):
        if not request.data.get('info'):
            raise CustomException(message='缺少info字段参数', code=40124, http_code=HTTP_400_BAD_REQUEST)
        print(request.data)
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj, data=request.data.get('info'), partial=True)
        if obj_serializer.is_valid(raise_exception=True):
            obj_serializer.save()
        return Response({'data': obj_serializer.data})
        # return Response({'data': 'asfasfsa'})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        return Response({'data': obj_serializer.data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        obj_serializer.destroy()
        return Response({'data': 'destroy success!'})


class AccessControlViewSet(ModelViewSet, CommonPagi):
    authentication_classes = []
    pagination_class = LimitOffsetPagination
    permission_classes = []
    renderer_classes = [CustomRenderer]
    serializer_class = serializer.AccessControlSerializer
    # only_update_fields = ['ctrl_name', 'remark', 'oper_id']

    def get_object(self, pk=None):
        try:
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        except Exception as exp:
            raise rest_framework.exceptions.NotFound(detail='对象没有找到')
        return obj

    def get_queryset(self):
        return models.UserctrlResrcOperation.objects.all()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        return Response({'data': self.get_paginated_data(qs, self)})

    def create(self, request, *args, **kwargs):
        """
        request.data = {
            'ctrl_name':'',
            'remark':'',
            'oper_code': '',
            'resrc_code': ''
        }

        """
        ctrl_serializer = self.get_serializer(data=request.data)
        if ctrl_serializer.is_valid(raise_exception=True):
            ctrl_serializer.save()
        return Response({'data': ctrl_serializer.data})

    def update(self, request: Request, *args, **kwargs):
        """
        request.data = {
            'ctrl_name':'',
            'remark':'',
            'oper_id': ''
        }
        """

        ctrl_obj = self.get_object(pk=kwargs.get('pk'))
        req_data = request.data
        req_data = dict(filter(lambda x: x in self.get_serializer_class().Meta.only_update_fields, req_data))
        ctrl_serializer = self.get_serializer(ctrl_obj, data=req_data, partial=True)
        if ctrl_serializer.is_valid(raise_exception=True):
            ctrl_serializer.save()
        return Response({'data': ctrl_serializer.data})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        return Response({'data': obj_serializer.data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        obj_serializer.destroy()
        return Response({'data': 'destroy success!'})


class GroupViewSet(ModelViewSet, CommonPagi):
    authentication_classes = []
    pagination_class = LimitOffsetPagination
    permission_classes = []
    renderer_classes = [CustomRenderer]
    serializer_class = serializer.GroupSerializer
    # lookup_field =
    # filterset_class =

    def get_object(self, pk=None):
        try:
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        except Exception as exp:
            raise rest_framework.exceptions.NotFound(detail='对象没有找到')
        return obj

    def get_object_with(self, **kwagrs):
        try:
            obj = get_object_or_404(self.get_queryset(), **kwagrs)
        except Exception as exp:
            return None
        return obj

    def get_queryset(self):
        return models.UserctrlUsergroup.objects.all()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        return Response({'data': self.get_paginated_data(qs, self)})

    def create(self, request, *args, **kwargs):
        """
        request.data = {
            'group_name':'',
        }
        """

        obj = self.get_object_with(group_name=request.data.get('group_name'))
        if not obj:
            req_data = request.data
            req_data['group_code'] = uuid.uuid3(uuid.uuid4(), req_data['group_name'])
            group_serializer = self.get_serializer(data=req_data)
            if group_serializer.is_valid(raise_exception=True):
                group_serializer.save()
            return Response({'data': group_serializer.data})
        raise CustomException(message='组名 `{0}` 已存在'.format(obj.group_name), code='repeat name',
                              http_code=HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args, **kwargs):
        """
        request.data = {
            'group_name':'',
            'remark': ''
        }
        """

        ctrl_obj = self.get_object(pk=kwargs.get('pk'))
        req_data = request.data
        if req_data.get('group_name'):
            req_data['group_code'] = uuid.uuid3(uuid.uuid4(), req_data['group_name'])
        ctrl_serializer = self.get_serializer(ctrl_obj, data=req_data, partial=True)
        if ctrl_serializer.is_valid(raise_exception=True):
            ctrl_serializer.save()
        return Response({'data': ctrl_serializer.data})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        return Response({'data': obj_serializer.data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        obj_serializer.destroy()
        return Response({'data': 'destroy success!'})


class GroupCtrlViewSet(ModelViewSet, CommonPagi):
    authentication_classes = []
    pagination_class = LimitOffsetPagination
    permission_classes = []
    renderer_classes = [CustomRenderer]
    serializer_class = serializer.GroupCtrlSerializer

    # lookup_field =
    # filterset_class =

    def get_object(self, pk=None):
        try:
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        except Exception as exp:
            raise rest_framework.exceptions.NotFound(detail='对象没有找到')
        return obj

    def get_object_with(self, **kwagrs):
        try:
            obj = get_object_or_404(self.get_queryset(), **kwagrs)
        except Exception as exp:
            return None
        return obj

    def get_queryset(self):
        return models.UserctrlUsergroupCtrl.objects.all()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        return Response({'data': self.get_paginated_data(qs, self)})

    def create(self, request, *args, **kwargs):
        """
        request.data = {
            'has_expect':'',
            'expect_time''',
            'is_on'
        }
        """

        obj = self.get_object_with(group_name=request.data.get('group_name'))
        if not obj:
            req_data = request.data
            req_data['group_code'] = uuid.uuid3(uuid.uuid4(), req_data['group_name'])
            group_serializer = self.get_serializer(data=req_data)
            if group_serializer.is_valid(raise_exception=True):
                group_serializer.save()
            return Response({'data': group_serializer.data})
        raise CustomException(message='组名 `{0}` 已存在'.format(obj.group_name), code='repeat name',
                              http_code=HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args, **kwargs):
        """
        request.data = {
            'group_name':'',
            'remark': ''
        }
        """

        ctrl_obj = self.get_object(pk=kwargs.get('pk'))
        req_data = request.data
        if req_data.get('group_name'):
            req_data['group_code'] = uuid.uuid3(uuid.uuid4(), req_data['group_name'])
        ctrl_serializer = self.get_serializer(ctrl_obj, data=req_data, partial=True)
        if ctrl_serializer.is_valid(raise_exception=True):
            ctrl_serializer.save()
        return Response({'data': ctrl_serializer.data})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        return Response({'data': obj_serializer.data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(pk=kwargs.get('pk'))
        obj_serializer = self.get_serializer(obj)
        obj_serializer.destroy()
        return Response({'data': 'destroy success!'})


class UserCtrlViewSet(ModelViewSet):
    pass


class UserViewSet(ModelViewSet):
    pass


class RoleCtrlViewSet(ModelViewSet):
    pass


class RoleViewSet(ModelViewSet):
    pass