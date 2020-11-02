from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site, Page
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from muni_portal.core.models import ServicePage, AdministratorPage


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
                response = self.client.get(self.url + f"{page.id}/")
                assert response.status_code == status.HTTP_200_OK


class ApiImagesTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        profile_image = Image.objects.create(
            file=get_test_image_file()
        )
        head_of_service = AdministratorPage.objects.create(
            title="Test AdministratorPage",
            slug="test-administrator-page",
            path="00011111",
            depth=2,
            profile_image=profile_image,
        )
        service_page = ServicePage(
            title="Test ServicePage",
            slug="test-service-page",
            path="00012222",
            depth=2,
            live=True,
            icon_classes=[],
            head_of_service=head_of_service
        )
        Site.objects.first().root_page.add_child(instance=service_page)
        response = self.client.get(self.url + f"{service_page.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["head_of_service"]["profile_image"]
        assert response.json()["head_of_service"]["profile_image_thumbnail"]
