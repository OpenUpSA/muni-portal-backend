# Generated by Django 2.2.10 on 2021-04-16 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20210416_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirectorpage',
            name='redirect_to',
            field=models.CharField(help_text='The URL to redirect to', max_length=500),
        ),
    ]