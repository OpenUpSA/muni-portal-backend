from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.core.models import Page, Orderable
from rest_framework import serializers as drf_serializers
from . import serializers
from rest_framework.fields import Field


NON_LINK_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "hr"]


class RelatedPagesSerializer(Field):
    @staticmethod
    def page_representation(page):
        return {
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'url': page.url,
            'icon_classes': page.icon_classes if hasattr(page, "icon_classes") else None,
        }

    def to_representation(self, pages):
        return [RelatedPagesSerializer.page_representation(page) for page in pages.specific()]


class HomePage(Page):
    subpage_types = [
        "core.ServicesIndexPage",
        "core.MyMuniPage",
    ]
    max_count_per_parent = 1


    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]

class ServicesIndexPage(Page):
    subpage_types = [
        "core.ServicePage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
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


class PersonContact(Orderable, models.Model):
    page = ParentalKey(
        "core.PersonPage", on_delete=models.CASCADE, related_name="person_contacts"
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "person contact"
        verbose_name_plural = "person contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class ContactDetailTypeManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ContactDetailType(models.Model):
    label = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    icon_classes = models.CharField(max_length=100, blank=True)

    objects = ContactDetailTypeManager()

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return self.label


class ContactDetailTypeSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ContactDetailType
        exclude = ["id"]


class ContactSerializer(drf_serializers.Serializer):
    value = drf_serializers.SerializerMethodField()
    type = serializers.SerializerMethodNestedSerializer(ContactDetailTypeSerializer)
    annotation = drf_serializers.SerializerMethodField()

    class Meta:
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


class PersonContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        model = PersonContact


class ServiceContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        model = ServiceContact


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
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
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


class PersonPage(Page):
    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("person_contacts", serializer=PersonContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


PersonPage._meta.get_field("title").verbose_name = "Name"


class CouncillorPage(PersonPage):
    subpage_types = []

    councillor_groups = ParentalManyToManyField('core.CouncillorGroupPage', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("councillor_groups"),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("councillor_groups"),
        APIField("person_contacts", serializer=PersonContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class CouncillorListPage(Page):
    subpage_types = [
        "core.CouncillorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class CouncillorGroupPage(Page):
    subpage_types = []

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class AdministratorPage(PersonPage):
    subpage_types = []


class AdministrationIndexPage(Page):
    subpage_types = [
        "core.AdministratorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class PoliticalRepsIndexPage(Page):
    subpage_types = [
        "core.CouncillorGroupPage",
        "core.CouncillorListPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class MyMuniPage(Page):
    subpage_types = [
        "core.PoliticalRepsIndexPage",
        "core.AdministrationIndexPage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]
