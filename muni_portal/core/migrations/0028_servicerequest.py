# Generated by Django 2.2.10 on 2021-02-22 12:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0027_auto_20210212_0804'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collaborator_object_id', models.PositiveIntegerField(help_text='The Object ID for this object in the Collaborator Web API')),
                ('type', models.CharField(blank=True, max_length=254, null=True)),
                ('user_name', models.CharField(max_length=254)),
                ('user_surname', models.CharField(max_length=254)),
                ('user_mobile_number', models.CharField(max_length=30)),
                ('user_email_address', models.EmailField(max_length=254)),
                ('municipal_account_number', models.CharField(blank=True, max_length=254, null=True)),
                ('street_name', models.CharField(max_length=254)),
                ('street_number', models.CharField(max_length=254)),
                ('suburb', models.CharField(max_length=254)),
                ('description', models.CharField(max_length=1024)),
                ('coordinates', models.CharField(blank=True, max_length=254, null=True)),
                ('request_date', models.DateField(default=None)),
                ('mobile_reference', models.CharField(blank=True, max_length=254, null=True)),
                ('on_premis_reference', models.CharField(blank=True, max_length=254, null=True)),
                ('status', models.CharField(blank=True, choices=[('queued', 'Queued'), ('created', 'Created'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default=None, max_length=254, null=True)),
                ('demarcation_code', models.CharField(blank=True, max_length=254, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]