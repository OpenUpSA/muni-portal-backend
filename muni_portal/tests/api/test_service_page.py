from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from muni_portal.core.models import (
    ServicePage, AdministratorPage, ServicePointPage
)

OFFICE_HOURS_TEST_TEXT = "<div>Office hours text</div>"


class ServicePageApiTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.first()

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
        # create page here to be able to reuse it in next tests
        cls.page = ServicePage(
            title="Test ServicePage",
            slug="test-service-page",
            path="00012222",
            depth=2,
            live=True,
            icon_classes=[],
            office_hours=OFFICE_HOURS_TEST_TEXT,
            head_of_service=head_of_service
        )
        cls.site.root_page.add_child(instance=cls.page)

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_serialisation(self):
        response = self.client.get(self.url + f"{self.page.id}/")
        res_as_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            "profile_image" in res_as_dict["head_of_service"],
            True
        )
        self.assertEqual(
            "profile_image_thumbnail" in res_as_dict["head_of_service"],
            True
        )
        self.assertEqual("office_hours" in res_as_dict, True)
        self.assertEqual(res_as_dict["office_hours"], OFFICE_HOURS_TEST_TEXT)


    def test_service_point_page_serialisation(self):
        service_point_page = ServicePointPage(
            title="Test ServicePointPage",
            slug="test-service-page",
            path="00012222",
            depth=2,
            office_hours=OFFICE_HOURS_TEST_TEXT,
        )
        self.page.add_child(instance=service_point_page)
        response = self.client.get(self.url + f"{service_point_page.id}/")
        res_as_dict = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("office_hours" in res_as_dict, True)
        self.assertEqual(res_as_dict["office_hours"], OFFICE_HOURS_TEST_TEXT)
