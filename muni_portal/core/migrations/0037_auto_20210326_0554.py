# Generated by Django 2.2.10 on 2021-03-26 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20210325_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencycontact',
            name='icon_classes',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='nationalgovernmentcontact',
            name='icon_classes',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='provincialgovernmentcontact',
            name='icon_classes',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
