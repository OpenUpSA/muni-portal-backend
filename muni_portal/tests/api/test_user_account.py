from django.contrib.auth.models import User
from django.core import mail
from django.test import Client as DjangoClient
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from urllib.parse import urlparse, parse_qsl


class ApiUserAccountTestCase(APITestCase):

    def setUp(self):
        self.password = Faker().password(length=8)

    def test_registration(self):
        data = {
            "email": "test@test.com",
            "username": "test",
            "password": self.password,
            "password_confirm": self.password
        }
        response = self.client.post(reverse("rest_registration:register"), data=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(len(mail.outbox), 1)

        verification_url = urlparse(mail.outbox[0].body)
        response = self.client.post(
            reverse("rest_registration:verify-registration"), data=dict(parse_qsl(verification_url.query))
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse("token_obtain_pair"), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_reset_password(self):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"email": user.email}
        response = self.client.post(reverse("rest_registration:send-reset-password-link"), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(mail.outbox), 1)

        verification_url = urlparse(mail.outbox[0].body)
        reset_password_data = dict(parse_qsl(verification_url.query))
        reset_password_data["password"] = Faker().password(length=8)
        response = self.client.post(reverse("rest_registration:reset-password"), data=reset_password_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        reset_password_data["username"] = user.username
        response = self.client.post(reverse("token_obtain_pair"), data=reset_password_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"login": user.username, "password": self.password}
        response = self.client.post(reverse("rest_registration:login"), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        jwt_token = response.data.get("token").get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        response = self.client.get(reverse("rest_registration:profile"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse("rest_registration:logout"), data={"revoke_token": True})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_profile(self):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"username": user.username, "password": self.password}
        response = self.client.post(reverse("token_obtain_pair"), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        jwt_token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        response = self.client.get(reverse("rest_registration:profile"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_profile_access_denied(self):
        response = self.client.get(reverse("rest_registration:profile"))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Create superuser, login and try to get profile from API without JWT token
        django_client = DjangoClient()
        user = User.objects.create_superuser(
            username="test", email="test@test.com", password=self.password
        )
        django_client.force_login(user)

        response = django_client.get(reverse("admin:index"), follow=True)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("rest_registration:profile"))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)