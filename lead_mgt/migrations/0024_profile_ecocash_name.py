# Generated by Django 2.1.3 on 2018-12-23 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0023_auto_20181222_0501'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ecocash_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]