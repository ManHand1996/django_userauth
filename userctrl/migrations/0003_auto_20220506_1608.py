# Generated by Django 3.2.6 on 2022-05-06 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userctrl', '0002_rename_resrc_name_userctrlresrc_type_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userctrlresourcetype',
            old_name='resrc_name',
            new_name='type_name',
        ),
        migrations.RenameField(
            model_name='userctrlresrc',
            old_name='type_name',
            new_name='resrc_name',
        ),
    ]
