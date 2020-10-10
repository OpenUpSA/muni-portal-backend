from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable
from rest_framework import serializers as drf_serializers
from . import serializers


NON_LINK_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "hr"]


class HomePage(Page):
    subpage_types = [
        "core.ServicesIndexPage",
    ]


class ServicesIndexPage(Page):
    subpage_types = [
        "core.ServicePage",
    ]


class ServiceContact(Orderable, models.Model):
    page = ParentalKey(
        "core.ServicePage", on_delete=models.CASCADE, related_name="service_contacts"
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "service contact"
        verbose_name_plural = "service contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class ContactDetailType(models.Model):
    label = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    icon_classes = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.label


class ContactDetailTypeSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ContactDetailType
        exclude = ["id"]


class ServiceContactSerializer(drf_serializers.Serializer):
    value = drf_serializers.SerializerMethodField()
    type = serializers.SerializerMethodNestedSerializer(ContactDetailTypeSerializer)
    annotation = drf_serializers.SerializerMethodField()

    class Meta:
        model = ServiceContact
        fields = [
            "value",
            "type",
            "annotation",
        ]
        depth = 1

    def get_value(self, obj):
        return obj.contact.value

    def get_type(self, obj):
        return obj.contact.type

    def get_annotation(self, obj):
        return obj.contact.annotation



class ServicePage(Page):
    subpage_types = []

    icon_classes = models.CharField(max_length=250)
    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        FieldPanel("overview"),
        InlinePanel("service_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField("overview"),
        APIField("service_contacts", serializer=ServiceContactSerializer(many=True)),
    ]


@register_snippet
class ContactDetail(models.Model):
    value = models.CharField(max_length=250)
    type = models.ForeignKey("ContactDetailType", on_delete=models.CASCADE)
    annotation = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text=('Optional public note of what this contact is for, e.g. '
                   '"Senior Library Assistant Ms A Jones" or "John Smith'
                   'Cell phone number"'),
    )
    purpose = models.CharField(
        max_length=250,
        help_text=('Internal reminder of what this represents - e.g. "Office '
                   'number for Joanne Smith"'),
    )

    panels = [
        FieldPanel("type"),
        FieldPanel("value"),
        FieldPanel("annotation"),
        FieldPanel("purpose"),
    ]

    def __str__(self):
        return f"{ self.value } ({ self.purpose })"
