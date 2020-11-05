from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from muni_portal.core.models import Webhook


class ApiWebhookTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("webhooks")
        self.user = User.objects.create(email="test@test.com")

    def test_api_webhook(self):
        self.client.force_authenticate(self.user)
        test_data = {"test": "test"}
        response = self.client.post(self.url, data=test_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Webhook.objects.first().data == test_data

    def test_api_webhook_not_authenticated(self):
        test_data = {"test": "test"}
        response = self.client.post(self.url, data=test_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
