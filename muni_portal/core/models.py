from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField


class HomePage(Page):
    subpage_types = [
        "core.ServicesIndexPage",
    ]


class ServicesIndexPage(Page):
    subpage_types = [
        "core.ServicePage",
    ]


class ServicePage(Page):
    subpage_types = []

    icon_classes = models.CharField(max_length=250)
    overview = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField("overview"),
    ]
