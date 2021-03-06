# Generated by Django 2.2.10 on 2021-03-25 16:19

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0052_pagelogentry'),
        ('core', '0034_auto_20210310_0922'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ProvincialGovernmentContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.ContactDetail')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='provincial_government_contacts', to='core.ContactsPage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NationalGovernmentContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.ContactDetail')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='national_government_contacts', to='core.ContactsPage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.ContactDetail')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to='core.ContactsPage')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
