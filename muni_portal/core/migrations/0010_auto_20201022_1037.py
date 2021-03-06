# Generated by Django 2.2.10 on 2020-10-22 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('core', '0009_administrationindexpage_overview'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoliticalParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('abbreviation', models.CharField(max_length=20)),
                ('logo_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
        ),
        migrations.AddField(
            model_name='councillorpage',
            name='political_party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.PoliticalParty'),
        ),
    ]
