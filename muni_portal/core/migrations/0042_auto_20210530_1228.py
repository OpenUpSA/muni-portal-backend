# Generated by Django 2.2.10 on 2021-05-30 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_merge_20210525_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='noticepage',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
