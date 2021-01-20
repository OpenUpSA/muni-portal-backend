from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from muni_portal.core.models import Webhook


class ApiWebhookTestCase(TestCase):

    def setUp(self):
        self.url = reverse("webhooks")
        self.user = User.objects.create(email="test@test.com")
        self.token = Token.objects.create(user=self.user)

    def test_api_webhook(self):
        client = APIClient()
        test_data = {"test": "test"}
        response = client.post(self.url, data=test_data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Webhook.objects.first().data, test_data)

    def test_api_webhook_not_authenticated(self):
        client = APIClient()
        test_data = {"test": "test"}
        response = client.post(self.url, data=test_data, HTTP_AUTHORIZATION=f"Bearer NONSENSE")
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(Webhook.objects.count(), 0)
