# Generated by Django 2.1.3 on 2018-12-08 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0019_auto_20181208_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawcalldata',
            name='current_next_call',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]