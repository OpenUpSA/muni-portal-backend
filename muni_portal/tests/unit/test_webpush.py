from django.contrib.auth.models import User
from django.test import TestCase
from faker import Faker
from pywebpush import WebPushException
from rest_framework import status
from unittest.mock import patch

from muni_portal.core.models import WebPushNotification, WebPushSubscription, WebPushNotificationResult
from muni_portal.core.signals import queue_send_webpush_notification
from muni_portal.tests import Response

faker = Faker()


class WebPushNotificationTestCase(TestCase):

    def setUp(self) -> None:
        self.password = faker.password(length=8)
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        self.subscription = WebPushSubscription.objects.create(
            user=self.user,
            subscription_object={
                "endpoint": faker.uri(),
                "keys": {
                    "auth": faker.pystr(min_chars=1, max_chars=100),
                    "p256dh": faker.pystr(min_chars=1, max_chars=100),
                },
                "some_future_key": faker.pystr(min_chars=1, max_chars=100),
            })
        self.notification = WebPushNotification.objects.create(
            status=WebPushNotification.STATUS_QUEUED,
            title=faker.sentence(),
            body=faker.paragraph(),
            url=faker.uri(),
        )

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification(self, webpush_mock):
        webpush_mock.return_value = Response(status_code=status.HTTP_200_OK, data={"message": "OK"})
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.subscription.refresh_from_db()
        self.notification.refresh_from_db()
        self.assertTrue(self.subscription.enabled)
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)

        result = WebPushNotificationResult.objects.first()
        self.assertEquals(result.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.message)

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification_failed(self, webpush_mock):
        def side_effect(*args, **kwargs):
            response = Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"content-type": "text/plain"}, text="Bad Request"
            )
            raise WebPushException("Bad Request", response=response)

        webpush_mock.side_effect = side_effect
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.subscription.refresh_from_db()
        self.notification.refresh_from_db()
        self.assertTrue(self.subscription.enabled)
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)

        result = WebPushNotificationResult.objects.first()
        self.assertEquals(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.message)

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification_disabled(self, webpush_mock):
        def side_effect(*args, **kwargs):
            response = Response(
                status_code=status.HTTP_410_GONE,
                headers={"content-type": "text/plain"}, text="User unsubscribed"
            )
            raise WebPushException("Gone", response=response)

        webpush_mock.side_effect = side_effect
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.subscription.refresh_from_db()
        self.notification.refresh_from_db()
        self.assertFalse(self.subscription.enabled)
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)

        result = WebPushNotificationResult.objects.first()
        self.assertEquals(result.status_code, status.HTTP_410_GONE)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.message)

    @patch("muni_portal.core.signals.webpush")
    def test_queue_send_webpush_notification_unhandled(self, webpush_mock):
        def side_effect(*args, **kwargs):
            raise Exception("Unhandled exception")

        webpush_mock.side_effect = side_effect
        send_webpush_result = queue_send_webpush_notification(self.notification.id)

        self.assertTrue(send_webpush_result)
        self.assertTrue(webpush_mock.called)

        self.subscription.refresh_from_db()
        self.notification.refresh_from_db()
        self.assertTrue(self.subscription.enabled)
        self.assertEquals(self.notification.status, WebPushNotification.STATUS_COMPLETED)

        result = WebPushNotificationResult.objects.first()
        self.assertIsNone(result.status_code)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.message)
