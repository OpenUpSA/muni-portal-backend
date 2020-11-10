from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from muni_portal.core.models import Webhook


class ApiWebhookTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("webhooks")
        self.user = User.objects.create(email="test@test.com")
        self.token = Token.objects.create(user=self.user)

    def test_api_webhook(self):
        self.client.force_authenticate(self.user, self.token)
        test_data = {"test": "test"}
        response = self.client.post(self.url, data=test_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Webhook.objects.first().data, test_data)

    def test_api_webhook_not_authenticated(self):
        test_data = {"test": "test"}
        response = self.client.post(self.url, data=test_data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
