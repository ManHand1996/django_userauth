# Generated by Django 3.2.6 on 2022-02-06 09:22

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseuser', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='用户名'),
        ),
    ]
