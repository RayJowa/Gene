# Generated by Django 2.1.3 on 2018-12-22 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0022_auto_20181208_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='close_status',
            field=models.CharField(blank=True, choices=[('unreachable', 'unreachable'), ('unreachable_follow_up', 'unreachable follow up'), ('wrong_number', 'wrong number'), ('converted', 'converted'), ('not_interested', 'not interested'), ('not_expired', 'not expired'), ('call_later', 'call later'), ('quoted', 'quoted'), ('bad_line', 'bad line')], max_length=30),
        ),
    ]
