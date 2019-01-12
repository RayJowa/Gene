# Generated by Django 2.1.3 on 2018-11-29 13:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lead_mgt', '0003_lead_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='agent',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL),
        ),
    ]