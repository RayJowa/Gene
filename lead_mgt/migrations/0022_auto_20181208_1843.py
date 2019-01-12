# Generated by Django 2.1.3 on 2018-12-08 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_mgt', '0021_auto_20181208_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheme_name', models.CharField(max_length=20)),
                ('level_0_comp', models.IntegerField()),
                ('level_1_comp', models.IntegerField()),
                ('level_2_comp', models.IntegerField()),
                ('level_3_comp', models.IntegerField()),
                ('level_0_ftp', models.IntegerField()),
                ('level_1_ftp', models.IntegerField()),
                ('level_2_ftp', models.IntegerField()),
                ('level_3_ftp', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='rawcalldata',
            name='policy_type',
            field=models.CharField(blank=True, choices=[('ftp', 'full third party'), ('comp', 'comprehensive')], max_length=20),
        ),
    ]