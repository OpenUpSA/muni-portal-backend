from django.conf import settings
from django.urls import reverse
from rest_framework import status

from muni_portal.core.models import WebPushSubscription
from muni_portal.core.serializers import WebpushSubscriptionSerializer
from muni_portal.tests.api import LoggedInUserTestCase


class ApiWebpushTestCase(LoggedInUserTestCase):

    def test_api_webpush(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.jwt_token}")
        test_data = {
            "subscription_object": {
                "endpoint": self.faker.uri(),
                "keys": {
                    "auth": self.faker.pystr(min_chars=1, max_chars=100),
                    "p256dh": self.faker.pystr(min_chars=1, max_chars=100),
                },
                "some_future_key": self.faker.pystr(min_chars=1, max_chars=100),
            }
        }
        response = self.client.post(reverse("webpush"), data=test_data, format="json")
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(WebPushSubscription.objects.first().user, self.user)
        serializer = WebpushSubscriptionSerializer(instance=WebPushSubscription.objects.first())
        self.assertEquals(serializer.data["subscription_object"], test_data["subscription_object"])

    def test_api_webpush_not_authenticated(self):
        response = self.client.post(reverse("webpush"), data={})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApiVapidTestCase(LoggedInUserTestCase):

    def test_api_webpush(self):
        response = self.client.get(reverse("vapid"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data["vapid_public_key"], settings.VAPID_PUBLIC_KEY)
