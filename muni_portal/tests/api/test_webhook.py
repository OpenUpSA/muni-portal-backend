from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json
from muni_portal.core.models import Webhook


class ApiWebhookTestCase(TestCase):
    """
    Ensure that authentication works using the bearer keyword.
    Ensure that the body object is actually stored.
    Ensure that nothing is stored when authentication fails, and a useful response is provided.
    """

    def setUp(self):
        self.url = reverse("webhooks")
        self.user = User.objects.create(email="test@test.com")
        self.token = Token.objects.create(user=self.user)

    def test_api_webhook(self):
        client = APIClient()
        test_data = {"testkey": "testvalue"}
        response = client.post(
            self.url,
            data=json.dumps(test_data),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        # Ensure response content type was JSON and value was "ok"
        self.assertEquals(response.json(), "success")
        self.assertEquals(Webhook.objects.first().data, test_data)

    def test_api_webhook_not_authenticated(self):
        client = APIClient()
        test_data = {"test": "test"}
        response = client.post(
            self.url,
            data=json.dumps(test_data),
            HTTP_AUTHORIZATION=f"Bearer NONSENSE",
            content_type="application/json",
        )
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(response.json()["detail"], "Invalid token.")
        self.assertEquals(Webhook.objects.count(), 0)
