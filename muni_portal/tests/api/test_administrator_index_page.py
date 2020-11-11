from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from muni_portal.core.models import AdministrationIndexPage, AdministratorPage


class ServicePageApiTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        profile_image = Image.objects.create(
            file=get_test_image_file()
        )
        administrator_page = AdministratorPage(
            title="Test AdministratorPage",
            slug="test-administrator-page",
            path="00011111",
            depth=2,
            profile_image=profile_image,
        )
        page = AdministrationIndexPage(
            title="Test ServicePage",
            slug="test-service-page",
            path="00012222",
            depth=2,
            live=True,
            overview="Test",
        )
        Site.objects.first().root_page.add_child(instance=page)
        page.add_child(instance=administrator_page)
        response = self.client.get(self.url + f"{page.id}/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json()["child_pages"][0]["profile_image"])
        self.assertIsNotNone(response.json()["child_pages"][0]["profile_image_thumbnail"])
