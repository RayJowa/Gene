# Generated by Django 2.1.3 on 2018-11-29 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0005_auto_20181129_1636'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Callback',
            new_name='Call',
        ),
    ]