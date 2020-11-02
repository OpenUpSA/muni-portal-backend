from django.test import Client, TestCase
from django.urls import reverse
from muni_portal.core.models import CouncillorGroupPage, PoliticalRepsIndexPage
from rest_framework import status
from wagtail.core.models import Site


class PoliticalRepsIndexPageApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        councillor_group_page = CouncillorGroupPage(
            title="Test CouncillorGroupPage",
            slug="test-councillor-group-page",
            path="00011111",
            depth=2,
            icon_classes=["test1", "test2"],
            overview="Test"
        )
        page = PoliticalRepsIndexPage(
            title="Test PoliticalRepsIndexPage",
            slug="test-political-reps-index-page",
            path="00012222",
            depth=2,
            live=True,
            overview="Test",
        )
        Site.objects.first().root_page.add_child(instance=page)
        page.add_child(instance=councillor_group_page)
        response = self.client.get(self.url + f"{page.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["child_pages"][0]["icon_classes"]
