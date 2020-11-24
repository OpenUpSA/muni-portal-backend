from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django_q.models import Success as SuccessTask
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from muni_portal.core.models import WebPushNotification, WebPushSubscription

faker = Faker()


class WebPushNotificationIntegrationTestCase(TestCase):

    def setUp(self):
        self.dj_client = Client()
        self.api_client = APIClient()
        self.password = faker.password(length=8)
        self.user = User.objects.create_superuser(
            username="test", email="test@test.com", password=self.password
        )

    @patch("pywebpush.WebPusher")
    def test_webpush_notification_flow(self, web_pusher_mock):
        # Login existing user
        data = {"login": self.user.username, "password": self.password}
        response = self.api_client.post(reverse("rest_registration:login"), data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Create subscription via API
        jwt_token = response.data.get("token")
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        subscription_data = {
            "endpoint": faker.uri(),
            "auth": faker.pystr(min_chars=1, max_chars=100),
            "p256dh": faker.pystr(min_chars=1, max_chars=100),
            "expiration_time": faker.date(),
        }
        response = self.api_client.post(reverse("webpush"), subscription_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(WebPushSubscription.objects.count(), 1)

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
        self.dj_client.force_login(self.user)

        response = self.dj_client.post(admin_add_notification_page, django_admin_form_data)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(WebPushNotification.objects.count(), 1)
        self.assertEquals(SuccessTask.objects.count(), 1)

        # Check webpush notification call
        web_pusher_mock.assert_called_with({
            "endpoint": subscription_data["endpoint"],
            "keys": {
                "auth": subscription_data["auth"],
                "p256dh": subscription_data["p256dh"],
            }
        }, verbose=False)
