from django.db import models
from django.conf import settings
# custom auth_user_model
User = settings.AUTH_USER_MODEL
# Create your models here.


class UserctrlApp(models.Model):
    id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=100)
    app_id = models.CharField(max_length=255, unique=True)
    app_secret = models.CharField(max_length=255)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_app'


class UserctrlResourcetype(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100, blank=True, null=True)
    resrc_table = models.CharField(max_length=100, default='')

    class Meta:
        managed = True
        db_table = 'userctrl_resourcetype'


class UserctrlResrc(models.Model):
    id = models.AutoField(primary_key=True)
    resrc_name = models.CharField(max_length=100)
    resrc_code = models.CharField(max_length=100, unique=True)
    resrc_type = models.ForeignKey(UserctrlResourcetype, models.DO_NOTHING)
    app = models.ForeignKey(UserctrlApp, models.CASCADE)

    class Meta:
        managed = True
        db_table = 'userctrl_resrc'


class UserctrlOperation(models.Model):
    id = models.AutoField(primary_key=True)
    oper_name = models.CharField(max_length=100)
    oper_code = models.CharField(max_length=128)

    class Meta:
        managed = True
        db_table = 'userctrl_operation'


class UserctrlResrcOperation(models.Model):
    id = models.AutoField(primary_key=True)
    ctrl_name = models.CharField(max_length=100)
    ctrl_code = models.CharField(max_length=100)
    oper = models.ForeignKey(UserctrlOperation, models.DO_NOTHING)
    resrc = models.ForeignKey(UserctrlResrc, on_delete=models.CASCADE)
    remark = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_resrc_operation'


class UserctrlBaseuserCtrl(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ctrl = models.ForeignKey(UserctrlResrcOperation, on_delete=models.CASCADE)
    has_expect = models.BooleanField()
    expect_time = models.DateTimeField(blank=True, null=True)
    is_on = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'userctrl_baseuser_ctrl'
        constraints = [models.UniqueConstraint(fields=['ctrl', 'user'], name='unique_ctrl_user')]


class UserctrlResrcdata(models.Model):
    id = models.AutoField(primary_key=True)
    data_name = models.CharField(max_length=100)
    api_url = models.CharField(max_length=255)
    end_type = models.CharField(max_length=20, blank=True, null=True)
    # resrc_type = models.ForeignKey(UserctrlResourcetype, models.DO_NOTHING)
    # app = models.ForeignKey(UserctrlApp, on_delete=models.CASCADE)
    resrc = models.ForeignKey(UserctrlResrc, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_resrcdata'


class UserctrlResrcelement(models.Model):
    id = models.AutoField(primary_key=True)
    ele_name = models.CharField(max_length=100)
    ele_id = models.CharField(max_length=128, blank=True, null=True)
    ele_class = models.CharField(max_length=128, blank=True, null=True)
    ele_tag = models.CharField(max_length=50)
    end_type = models.CharField(max_length=20, blank=True, null=True)
    # resrc_type = models.ForeignKey(UserctrlResourcetype, models.DO_NOTHING)
    # app = models.ForeignKey(UserctrlApp, on_delete=models.CASCADE)
    resrc = models.ForeignKey(UserctrlResrc, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_resrcelement'


class UserctrlResrcfile(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    end_type = models.CharField(max_length=20, blank=True, null=True)
    # resrc_type = models.ForeignKey(UserctrlResourcetype, models.DO_NOTHING)
    # app = models.ForeignKey(UserctrlApp, on_delete=models.CASCADE)
    resrc = models.ForeignKey(UserctrlResrc, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_resrcfile'


class UserctrlResrcmenu(models.Model):
    id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=100)
    target_url = models.CharField(max_length=255)
    parent_id = models.IntegerField(blank=True, null=True)
    end_type = models.CharField(max_length=20, blank=True, null=True)
    # resrc_type = models.ForeignKey(UserctrlResourcetype, models.DO_NOTHING)
    # app = models.ForeignKey(UserctrlApp, on_delete=models.CASCADE)
    resrc = models.ForeignKey(UserctrlResrc, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_resrcmenu'


class UserctrlRole(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    role_code = models.CharField(unique=True, max_length=100)
    parent_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_role'


class UserctrlRoleBaseuser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(UserctrlRole, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'userctrl_role_baseuser'


class UserctrlRoleCtrl(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(UserctrlRole, on_delete=models.CASCADE)
    ctrl = models.ForeignKey(UserctrlResrcOperation, on_delete=models.CASCADE)
    has_expect = models.BooleanField()
    expect_time = models.DateTimeField(blank=True, null=True)
    is_on = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'userctrl_role_ctrl'

        constraints = [models.UniqueConstraint(fields=['role', 'ctrl'], name='unique_ctrl_role')]


class UserctrlUsergroup(models.Model):
    id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100)
    group_code = models.CharField(unique=True, max_length=100)
    remark = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userctrl_usergroup'


class UserctrlUsergroupBaseuser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(UserctrlUsergroup, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'userctrl_usergroup_baseuser'


class UserctrlUsergroupCtrl(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(UserctrlUsergroup, on_delete=models.CASCADE)
    ctrl = models.ForeignKey(UserctrlResrcOperation, on_delete=models.CASCADE)
    has_expect = models.BooleanField()
    expect_time = models.DateTimeField(blank=True, null=True)
    is_on = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'userctrl_usergroup_ctrl'
        constraints = [models.UniqueConstraint(fields=['ctrl', 'group'], name='unique_ctrl_group')]