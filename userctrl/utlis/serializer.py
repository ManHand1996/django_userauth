"""
object serializer for restful api
"""
from rest_framework import serializers
from userctrl import models
from rest_framework.fields import (  # NOQA # isort:skip
    empty
)


class AppSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return models.UserctrlApp.objects.create(**validated_data)

    def destroy(self):

        return self.instance.delete()

    class Meta:
        model = models.UserctrlApp
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    """
    资源序列化器
    """
    resrc_name = serializers.CharField(source='resrc.resrc_name', read_only=True)
    app_name = serializers.CharField(source='resrc.app.app_name', read_only=True)
    resrc_type = serializers.CharField(source='resrc.resrc_type.type_name', read_only=True)
    # resrcss = serializers.RelatedField(read_only=True)
    # resrc_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        print('validated data:', validated_data)
        return self.Meta.model.objects.create(**validated_data)

    def destroy(self):
        return self.instance.delete()

    def validate_end_type(self, val):
        """
        validate_field 对特等字段进行值校验
        :param val:
        :type val:
        :return:
        :rtype:
        """
        if val not in ('frontend', 'backend'):
            raise serializers.ValidationError("end_type 必须是 `frontend/backend` 之一")
        return val

    def to_representation(self, instance):
        """
        rewrite to_representation() drop resrc id
        :param instance:
        :type instance:
        :return:
        :rtype:
        """
        ret = super(ResourceSerializer, self).to_representation(instance)
        ret.pop('resrc')

        return ret

    class Meta:
        model = None
        fields = '__all__'
        depth = 0  # 显示对象深度 如包含外健的对象,可以直接显示该外健的所有属性


class AccessControlSerializer(serializers.ModelSerializer):

    oper_name = serializers.CharField(source='oper.oper_name', read_only=True)
    resrc_name = serializers.CharField(source='resrc.resrc_name', read_only=True)

    def create(self, validated_data):

        try:
            resrc = models.UserctrlResrc.objects.get(resrc_code=validated_data.get('resrc_code'))
            oper = models.UserctrlOperation.objects.get(oper_code=validated_data.get('oper_code'))
            validated_data['resrc_id'] = resrc.id
            validated_data['oper_id'] = oper.id
            return models.UserctrlResrcOperation.objects.create(**validated_data)
        except Exception as exp:
            raise serializers.ValidationError(detail='either resrc_code or oper_code is not exist')

    def destroy(self):
        return self.instance.delete()

    def to_representation(self, instance):
        ret = super(AccessControlSerializer, self).to_representation(instance)
        ret.pop('oper')
        ret.pop('resrc')
        return ret
    
    class Meta:
        model = models.UserctrlResrcOperation
        fields = '__all__'
        only_update_fields = ['ctrl_name', 'remark', 'oper_id']


class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return models.UserctrlUsergroup.objects.create(**validated_data)

    def destroy(self):
        return self.instance.delete()

    class Meta:
        model = models.UserctrlUsergroup
        fields = '__all__'


class GroupCtrlSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return models.UserctrlUsergroupCtrl.objects.create(**validated_data)

    def destroy(self):
        return self.instance.delete()

    class Meta:
        model = models.UserctrlUsergroupCtrl
        fields = '__all__'

if __name__ == '__main__':
    ser = AppSerializer()
    print(repr(ser))
