import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django_q.models import Success as SuccessTask
from faker import Faker
from py_vapid import Vapid
from rest_framework import status
from unittest.mock import patch

from muni_portal.core.models import WebPushNotification, WebPushSubscription

faker = Faker()
vapid = Vapid()


class WebPushNotificationIntegrationTestCase(TestCase):

    def setUp(self):
        self.password = faker.password(length=8)
        self.user = User.objects.create_superuser(
            username="test", email="test@test.com", password=self.password
        )
        vapid.generate_keys()
        vapid.save_key("private_key.pem")
        vapid.save_public_key("public_key.pem")

    def tearDown(self):
        os.remove("private_key.pem")
        os.remove("public_key.pem")

    @patch("pywebpush.WebPusher")
    def test_webpush_notification_flow(self, web_pusher_mock):
        subscription = WebPushSubscription.objects.create(
            user=self.user,
            endpoint=faker.uri(),
            auth=faker.pystr(min_chars=1, max_chars=100),
            p256dh=faker.pystr(min_chars=1, max_chars=100),
            expiration_time=faker.date(),
        )

        # Create and send notification via Django admin
        admin_add_notification_page = reverse(
            f"admin:{WebPushNotification._meta.app_label}_{WebPushNotification._meta.model_name}_add"
        )
        django_admin_form_data = {
            "status": WebPushNotification.STATUS_QUEUED,
            "title": faker.sentence(),
            "body": faker.paragraph(),
            "url": faker.uri(),
        }
        self.client.force_login(self.user)

        with self.settings(VAPID_PRIVATE_KEY="private_key.pem"):
            response = self.client.post(admin_add_notification_page, django_admin_form_data)

        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(WebPushNotification.objects.count(), 1)
        self.assertEquals(SuccessTask.objects.count(), 1)

        # Check webpush notification call
        web_pusher_mock.assert_called_with({
            "endpoint": subscription.endpoint,
            "keys": {
                "auth": subscription.auth,
                "p256dh": subscription.p256dh,
            }
        }, verbose=False)
