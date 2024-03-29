# Generated by Django 3.2.6 on 2022-05-08 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userctrl', '0007_userctrlrolectrl_unique_ctrl_role'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='userctrlbaseuserctrl',
            constraint=models.UniqueConstraint(fields=('ctrl', 'user'), name='unique_ctrl_user'),
        ),
        migrations.AddConstraint(
            model_name='userctrlusergroupctrl',
            constraint=models.UniqueConstraint(fields=('ctrl', 'group'), name='unique_ctrl_group'),
        ),
    ]
