# Generated by Django 2.1.3 on 2018-12-05 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0011_auto_20181205_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='user',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='interaction',
            name='lead',
            field=models.CharField(max_length=10),
        ),
    ]
