from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from muni_portal.core.models import CouncillorListPage, CouncillorPage, NoticeIndexPage, NoticePage


class NoticeIndexPageApiTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("wagtailapi:pages:listing")

    def test_service_page_image(self):
        notice_page_01 = NoticePage(
            title="Test NoticePage 01",
            slug="test-notice-page-01",
            body="<p>body</p>",
            path="00011111",
            depth=2,
        )
        notice_page_02 = NoticePage(
            title="Test NoticePage 02",
            slug="test-notice-page-02",
            body="<p>body</p>",
            path="00011111",
            depth=2,
        )
        page = NoticeIndexPage(
            title="Test NoticeIndexPage",
            slug="test-notice-index-page",
            path="00012222",
            depth=2,
            live=True,
        )
        Site.objects.first().root_page.add_child(instance=page)
        page.add_child(instance=notice_page_01)
        page.add_child(instance=notice_page_02)
        notice_page_01.save_revision().publish()
        notice_page_02.save_revision().publish()

        response = self.client.get(self.url + f"{page.id}/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        child_pages = response.json()["child_pages"]
        assert child_pages[1]["publication_date"] < child_pages[0]["publication_date"]

        response = self.client.get(self.url + f"{notice_page_01.id}/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()["body"], "<p>body</p>")
        self.assertEquals(response.json()["body_html"], "<p>body</p>")
