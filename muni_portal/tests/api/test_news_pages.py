from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site

from muni_portal.core.models import NewsIndexPage, NewsPage


class NewsIndexPageApiTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('wagtailapi:pages:listing')

    def test_pages(self):
        news_page_01 = NewsPage(
            title="Test NewsPage 01",
            subtitle="Test NewsPage 01",
            slug="test-news-page-01",
            body="<p>body</p>",
            path="00011111",
            depth=2,
        )
        news_page_02 = NewsPage(
            title="Test NewsPage 02",
            subtitle="Test NewsPage 02",
            slug="test-news-page-02",
            body="<p>body</p>",
            path="00011111",
            depth=2,
        )
        page = NewsIndexPage(
            title="Test NewsIndexPage",
            slug="test-news-index-page",
            path="00012222",
            depth=2,
            live=True,
        )
        Site.objects.first().root_page.add_child(instance=page)
        page.add_child(instance=news_page_01)
        page.add_child(instance=news_page_02)
        news_page_01.save_revision().publish()
        news_page_02.save_revision().publish()

        response = self.client.get(self.url + f"{page.id}/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        child_pages = response.json()["child_pages"]
        self.assertTrue(child_pages[1]["publication_date"] < child_pages[0]["publication_date"])

        response = self.client.get(self.url + f"{news_page_01.id}/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()["body"], "<p>body</p>")
        self.assertEquals(response.json()["body_html"], "<p>body</p>")
