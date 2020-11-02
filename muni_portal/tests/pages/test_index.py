from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class IndexPagesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get(reverse("index"))
        assert response.status_code == status.HTTP_200_OK
        assert "This is the homepage for muni_portal" in response.rendered_content

    def test_notification_index(self):
        response = self.client.get(reverse("notifications"))
        assert response.status_code == status.HTTP_200_OK
        assert "This is the index for notifications in muni_portal" in response.rendered_content
