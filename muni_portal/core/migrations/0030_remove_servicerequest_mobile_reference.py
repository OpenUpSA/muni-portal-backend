# Generated by Django 2.2.10 on 2021-02-24 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20210224_0936'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicerequest',
            name='mobile_reference',
        ),
    ]