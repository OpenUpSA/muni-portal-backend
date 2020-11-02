from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from muni_portal.core.models import CouncillorListPage, CouncillorPage


class CouncillorListPageApiTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        profile_image = Image.objects.create(
            file=get_test_image_file()
        )
        councillor_page = CouncillorPage(
            title="Test CouncillorPage",
            slug="test-councillor-page",
            path="00011111",
            depth=2,
            profile_image=profile_image,
        )
        page = CouncillorListPage(
            title="Test CouncillorListPage",
            slug="test-councillor-list-page",
            path="00012222",
            depth=2,
            live=True,
            overview="Test",
        )
        Site.objects.first().root_page.add_child(instance=page)
        page.add_child(instance=councillor_page)
        response = self.client.get(self.url + f"{page.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["child_pages"][0]["profile_image"]
        assert response.json()["child_pages"][0]["profile_image_thumbnail"]
