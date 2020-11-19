from django.contrib.auth.models import User
from django.test import TestCase
from faker import Faker
from pywebpush import WebPushException
from rest_framework import status
from unittest.mock import patch

from muni_portal.core.models import WebPushNotification, WebPushSubscription, WebPushNotificationResult
from muni_portal.core.signals import queue_send_webpush_notification

faker = Faker()


class WebPushNotificationTestCase(TestCase):

    def setUp(self) -> None:
        self.password = faker.password(length=8)
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        self.subscription = WebPushSubscription.objects.create(
            user=self.user,
            endpoint=faker.uri(),
            auth=faker.pystr(max_chars=32),
            p256dh=faker.pystr(max_chars=32),
        )
        self.notification = WebPushNotification.objects.create(
            status=WebPushNotification.STATUS_QUEUED,
            title=faker.sentence(),
            body=faker.paragraph(),
            url=faker.uri(),
        )

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification(self, webpush_mock):
        webpush_mock.return_value.status_code = status.HTTP_200_OK
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.notification.refresh_from_db()
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)
        self.assertEquals(WebPushNotificationResult.objects.first().status_code, status.HTTP_200_OK)

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification_failed(self, webpush_mock):
        class Response:
            def __init__(self, status_code=200):
                self.status_code = status_code

            def json(self):
                return {"status_code": self.status_code}

        def side_effect(*args, **kwargs):
            response = Response(status_code=400)
            raise WebPushException("Bad Request", response=response)

        webpush_mock.side_effect = side_effect
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.notification.refresh_from_db()
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)
        self.assertEquals(WebPushNotificationResult.objects.first().status_code, status.HTTP_400_BAD_REQUEST)
