# Generated by Django 2.2.10 on 2021-03-01 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20210224_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='request_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
