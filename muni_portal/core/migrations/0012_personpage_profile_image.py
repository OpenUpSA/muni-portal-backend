# Generated by Django 2.2.10 on 2020-10-22 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('core', '0011_auto_20201022_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='personpage',
            name='profile_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]