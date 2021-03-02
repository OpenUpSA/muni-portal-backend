# Generated by Django 2.2.10 on 2021-02-24 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_remove_servicerequest_mobile_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='collaborator_object_id',
            field=models.PositiveIntegerField(blank=True, help_text='The Object ID for this object in the Collaborator Web API', null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='description',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='request_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='street_name',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='street_number',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='suburb',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='user_email_address',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='user_mobile_number',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='user_name',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='user_surname',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]