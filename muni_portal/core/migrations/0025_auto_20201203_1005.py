# Generated by Django 2.2.10 on 2020-12-03 10:05

import django.contrib.postgres.fields.jsonb
from django.db import migrations


def migrate_subscriptions(apps, schema_editor):
    WebPushSubscription = apps.get_model('core', 'WebPushSubscription')
    for row in WebPushSubscription.objects.all():
        row.subscription_object = {
            "endpoint": row.endpoint,
            "keys": {
                "auth": row.auth,
                "p256dh": row.p256dh,
            },
            "expiration_time": row.expiration_time
        }
        row.save(update_fields=['subscription_object'])


def migrate_subscriptions_reverse(apps, schema_editor):
    WebPushSubscription = apps.get_model('core', 'WebPushSubscription')
    for row in WebPushSubscription.objects.all():
        row.endpoint = row.subscription_object["endpoint"]
        row.auth = row.subscription_object["keys"]["auth"]
        row.p256dh = row.subscription_object["keys"]["p256dh"]
        row.expiration_time = row.subscription_object["expiration_time"]

        row.save(update_fields=['endpoint', 'auth', 'p256dh', 'expiration_time'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_noticeindexpage_noticepage'),
    ]


    operations = [
        migrations.AddField(
            model_name='webpushsubscription',
            name='subscription_object',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='FOOBAR'),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_subscriptions, reverse_code=migrate_subscriptions_reverse),
        migrations.RemoveField(
            model_name='webpushsubscription',
            name='auth',
        ),
        migrations.RemoveField(
            model_name='webpushsubscription',
            name='endpoint',
        ),
        migrations.RemoveField(
            model_name='webpushsubscription',
            name='expiration_time',
        ),
        migrations.RemoveField(
            model_name='webpushsubscription',
            name='p256dh',
        ),
    ]