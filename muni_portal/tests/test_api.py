import logging

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site

logger = logging.getLogger(__name__)


class ApiTestCase(TestCase):
    fixtures = ("seeddata.json", "demodata.json",)

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_index(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_pages(self):
        for site in Site.objects.all():
            for page in site.root_page.get_descendants():
                logger.info(f"Testing page {page.title}")
                response = self.client.get(self.url + f"{page.id}/")
                assert response.status_code == status.HTTP_200_OK
