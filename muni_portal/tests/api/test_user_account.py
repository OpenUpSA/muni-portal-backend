from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from urllib.parse import urlparse, parse_qsl


class ApiUserAccountTestCase(APITestCase):

    def setUp(self):
        self.password = Faker().password(length=8)

    @patch("rest_registration.notifications.email.send_notification")
    @patch("rest_registration.notifications.email.create_verification_notification")
    def test_registration(self, create_verification_notification_mock, send_notification_mock):
        data = {
            "email": "test@test.com",
            "username": "test",
            "password": self.password,
            "password_confirm": self.password
        }
        response = self.client.post(reverse("rest_registration:register"), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert send_notification_mock.called

        verification_url = urlparse(
            create_verification_notification_mock.call_args[0][3]["params_signer"].get_url()
        )
        response = self.client.post(verification_url.path, data=dict(parse_qsl(verification_url.query)))
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post(reverse("token_obtain_pair"), data=data)
        assert response.status_code == status.HTTP_200_OK

    @patch("rest_registration.notifications.email.send_notification")
    @patch("rest_registration.notifications.email.create_verification_notification")
    def test_reset_password(self, create_verification_notification_mock, send_notification_mock):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"email": user.email}
        response = self.client.post(reverse("rest_registration:send-reset-password-link"), data=data)
        assert response.status_code == status.HTTP_200_OK
        assert send_notification_mock.called

        verification_url = urlparse(
            create_verification_notification_mock.call_args[0][3]["params_signer"].get_url()
        )
        reset_password_data = dict(parse_qsl(verification_url.query))
        reset_password_data["password"] = Faker().password(length=8)
        response = self.client.post(verification_url.path, data=reset_password_data)
        assert response.status_code == status.HTTP_200_OK

        reset_password_data["username"] = user.username
        response = self.client.post(reverse("token_obtain_pair"), data=reset_password_data)
        assert response.status_code == status.HTTP_200_OK

    def test_login(self):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"login": user.username, "password": self.password}
        response = self.client.post(reverse("rest_registration:login"), data=data)
        assert response.status_code == status.HTTP_200_OK

        jwt_token = response.data.get("token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        response = self.client.get(reverse("rest_registration:profile"))
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post(reverse("rest_registration:logout"), data={"revoke_token": True})
        assert response.status_code == status.HTTP_200_OK

    def test_profile(self):
        user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"username": user.username, "password": self.password}
        response = self.client.post(reverse("token_obtain_pair"), data=data)
        assert response.status_code == status.HTTP_200_OK

        jwt_token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        response = self.client.get(reverse("rest_registration:profile"))
        assert response.status_code == status.HTTP_200_OK

    def test_profile_access_denied(self):
        response = self.client.get(reverse("rest_registration:profile"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
