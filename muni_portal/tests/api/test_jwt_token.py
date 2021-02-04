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

    def test_refresh_token(self):
        login_data = {"username": self.user.username, "password": self.password}
        login_response = self.client.post(reverse("token_obtain_pair"), data=login_data)
        self.assertIn("refresh", login_response.data)

        refresh_data = {"refresh": login_response.data.get("refresh")}
        refresh_response = self.client.post(reverse("token_refresh"), data=refresh_data)
        self.assertEquals(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_invalid_refresh_token_fail(self):
        login_data = {"username": self.user.username, "password": self.password}
        self.client.post(reverse("token_obtain_pair"), data=login_data)

        refresh_data = {"refresh": "invalid refresh token"}
        refresh_response = self.client.post(reverse("token_refresh"), data=refresh_data)
        self.assertEquals(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
