from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class IndexPagesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("This is the homepage for muni_portal", response.rendered_content)

    def test_notification_index(self):
        response = self.client.get(reverse("notifications"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("This is the index for notifications in muni_portal", response.rendered_content)
