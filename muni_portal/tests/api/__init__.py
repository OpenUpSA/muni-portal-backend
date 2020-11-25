from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.test import APIClient


class LoggedInUserTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.faker = Faker()
        self.password = self.faker.password(length=8)
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password=self.password
        )
        data = {"login": self.user.username, "password": self.password}
        response = self.client.post(reverse("rest_registration:login"), data=data)
        self.jwt_token = response.data.get("token")
