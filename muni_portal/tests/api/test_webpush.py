from django.conf import settings
from django.urls import reverse
from rest_framework import status

from muni_portal.core.models import WebPushSubscription
from muni_portal.tests.api import LoggedInUserTestCase

import json
class ApiWebpushTestCase(LoggedInUserTestCase):

    def test_api_webpush(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.jwt_token}")
        test_subscription = {
            "endpoint": self.faker.uri(),
            "keys": {
                "auth": self.faker.pystr(min_chars=1, max_chars=100),
                "p256dh": self.faker.pystr(min_chars=1, max_chars=100),
            },
            "some_future_key": self.faker.pystr(min_chars=1, max_chars=100),
        }
        test_data = {
            "subscription_object": test_subscription
        }

        response = self.client.post(reverse("webpush"), data=json.dumps(test_data), content_type="application/json")

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(WebPushSubscription.objects.first().user, self.user)
        self.assertEquals(WebPushSubscription.objects.first().subscription_object, test_subscription)

    def test_api_webpush_not_authenticated(self):
        response = self.client.post(reverse("webpush"), data={})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApiVapidTestCase(LoggedInUserTestCase):

    def test_api_webpush(self):
        response = self.client.get(reverse("vapid"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["vapid_public_key"], settings.VAPID_PUBLIC_KEY)
