from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from muni_portal.core.models import Webpush
from muni_portal.core.serializers import WebpushSerializer


class ApiWebpushTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.faker = Faker()
        self.url = reverse("webpush")
        self.password = self.faker.password(length=8)
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"login": self.user.username, "password": self.password}
        response = self.client.post(reverse("rest_registration:login"), data=data)
        self.jwt_token = response.data.get("token")

    def test_api_webpush(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.jwt_token}")
        test_data = {
            "endpoint": self.faker.uri(),
            "auth": self.faker.pystr(min_chars=1, max_chars=100),
            "p256dh": self.faker.pystr(min_chars=1, max_chars=100),
            "expiration_time": self.faker.date(),
        }
        response = self.client.post(self.url, data=test_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Webpush.objects.first().user, self.user)

        serializer = WebpushSerializer(instance=Webpush.objects.first())
        self.assertEquals(serializer.data, test_data)

    def test_api_webpush_not_authenticated(self):
        response = self.client.post(self.url, data={})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
