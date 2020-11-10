from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from rest_framework import status


class ApiJWTTokenTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = Faker().password(length=8)
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )

    def test_token_obtain_pair(self):
        data = {"username": self.user.username, "password": self.password}
        response = self.client.post(reverse("token_obtain_pair"), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        response = self.client.post(reverse("token_refresh"), data=response.data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
