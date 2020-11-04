from django.test import Client, TestCase
from django.urls import reverse
from muni_portal.core.models import CouncillorGroupPage, PoliticalRepsIndexPage, CouncillorPage
from rest_framework import status
from wagtail.core.models import Site


class PoliticalRepsIndexPageApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        councillor_page = CouncillorPage.objects.create(
            title="Test CouncillorPage",
            slug="test-councillor-page",
            path="00011111111",
            depth=2,
        )
        councillor_group_page = CouncillorGroupPage(
            title="Test CouncillorGroupPage",
            slug="test-councillor-group-page",
            path="00011111",
            depth=2,
            icon_classes="test1 test2",
            overview="Test",
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
        councillor_group_page.councillors.add(councillor_page)
        response = self.client.get(self.url + f"{page.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["child_pages"][0]["icon_classes"] == "test1 test2"
        assert response.json()["child_pages"][0]["councillors_count"] == 1
