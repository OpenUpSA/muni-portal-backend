from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from rest_framework import serializers as drf_serializers
from rest_framework.fields import DateTimeField

from muni_portal.core.wagtail_serializers import (
    RelatedPagesSerializer,
    RelatedPersonPageSerializer,
    RelatedPersonPageListSerializer,
    SerializerMethodNestedSerializer,
    APIRichTextSerializer,
    RelatedCouncillorGroupPageSerializer,
    RichTextFieldSerializer,
    RelatedNoticePagesSerializer,
)
from django.shortcuts import redirect
from django.utils.html import format_html
import uuid

from django.contrib.auth.models import User

""" HERE BE DRAGONS!

 We want the User's email to be unique, but we're already into an existing project so creating a new custom User
 class is a bit of a mission. Instead, we use this hack to make this one tiny change for now.
 
 See https://stackoverflow.com/a/12708590 about this solution
 See https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#auth-custom-user and 
 https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-AUTH_USER_MODEL about the proper solutions and 
 the complications involved.
"""
User._meta.get_field('email')._unique = True

NON_LINK_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "hr"]
NON_IMAGE_FEATURES = NON_LINK_FEATURES + ["link"]
NON_EMBEDS_FEATURES = NON_IMAGE_FEATURES + ["image"]


class APIRichTextField(APIField):
    def __init__(self, name):
        serializer = APIRichTextSerializer()
        super().__init__(name=name, serializer=serializer)


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


class ServicePointContact(Orderable, models.Model):
    page = ParentalKey(
        "core.ServicePointPage",
        on_delete=models.CASCADE,
        related_name="service_point_contacts",
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "service point contact"
        verbose_name_plural = "service point contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class KeyContact(Orderable, models.Model):
    icon_classes = models.CharField(max_length=100, blank=True)
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("icon_classes"),
        SnippetChooserPanel("contact"),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.page.title + " -> " + self.contact


class EmergencyContact(KeyContact):
    page = ParentalKey(
        "core.ContactsPage", on_delete=models.CASCADE, related_name="emergency_contacts"
    )


class ProvincialGovernmentContact(KeyContact):
    page = ParentalKey(
        "core.ContactsPage",
        on_delete=models.CASCADE,
        related_name="provincial_government_contacts",
    )


class NationalGovernmentContact(KeyContact):
    page = ParentalKey(
        "core.ContactsPage",
        on_delete=models.CASCADE,
        related_name="national_government_contacts",
    )


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


class Webhook(models.Model):
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class ContactDetailTypeSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ContactDetailType
        exclude = ["id"]


class ContactSerializer(drf_serializers.Serializer):
    value = drf_serializers.SerializerMethodField()
    type = SerializerMethodNestedSerializer(ContactDetailTypeSerializer)
    annotation = drf_serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.contact.value

    def get_type(self, obj):
        return obj.contact.type

    def get_annotation(self, obj):
        return obj.contact.annotation


class KeyContactSerializer(ContactSerializer):
    icon_classes = drf_serializers.SerializerMethodField()

    def get_icon_classes(self, obj):
        return obj.icon_classes


@register_snippet
class ContactDetail(models.Model):
    value = models.CharField(max_length=250)
    type = models.ForeignKey("ContactDetailType", on_delete=models.CASCADE)
    annotation = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text=(
            "Optional public note of what this contact is for, e.g. "
            '"Senior Library Assistant Ms A Jones" or "John Smith'
            'Cell phone number"'
        ),
    )
    purpose = models.CharField(
        max_length=250,
        help_text=(
            'Internal reminder of what this represents - e.g. "Office '
            'number for Joanne Smith"'
        ),
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
    job_title = models.CharField(max_length=200, blank=True)
    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    profile_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("job_title"),
        FieldPanel("overview"),
        ImageChooserPanel("profile_image"),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("job_title"),
        APIField("overview"),
        APIField("profile_image"),
        APIField(
            "profile_image_thumbnail",
            ImageRenditionField("max-100x100", source="profile_image"),
        ),
        APIField("person_contacts", serializer=ContactSerializer(many=True)),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


PersonPage._meta.get_field("title").verbose_name = "Name"


@register_snippet
class PoliticalParty(models.Model):
    name = models.CharField(max_length=1000)
    abbreviation = models.CharField(max_length=20)
    logo_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("abbreviation"),
        ImageChooserPanel("logo_image"),
    ]

    class Meta:
        verbose_name_plural = "Political parties"

    def __str__(self):
        return self.name


class PoliticalPartySerializer(drf_serializers.ModelSerializer):
    logo_image_tumbnail = ImageRenditionField("max-100x100", source="logo_image")

    class Meta:
        model = PoliticalParty
        exclude = ["id"]
        depth = 1


class CouncillorPage(PersonPage):
    subpage_types = []

    political_party = models.ForeignKey(
        "core.PoliticalParty",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    councillor_groups = ParentalManyToManyField(
        "core.CouncillorGroupPage", blank=True, related_name="councillors"
    )

    content_panels = Page.content_panels + [
        FieldPanel("job_title"),
        FieldPanel("overview"),
        ImageChooserPanel("profile_image"),
        SnippetChooserPanel("political_party"),
        FieldPanel("councillor_groups"),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("job_title"),
        APIField("overview"),
        APIField("profile_image"),
        APIField(
            "profile_image_thumbnail",
            ImageRenditionField("max-100x100", source="profile_image"),
        ),
        APIField("political_party", serializer=PoliticalPartySerializer()),
        APIField("councillor_groups"),
        APIField("person_contacts", serializer=ContactSerializer(many=True)),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class CouncillorListPage(Page):
    subpage_types = [
        "core.CouncillorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)
    icon_classes = models.CharField(max_length=250, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("icon_classes"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("icon_classes"),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages",
            serializer=RelatedPersonPageListSerializer(source="get_children.live"),
        ),
    ]


class CouncillorGroupPage(Page):
    subpage_types = []

    overview = RichTextField(features=NON_LINK_FEATURES)
    icon_classes = models.CharField(max_length=250)
    members_label = models.CharField(
        max_length=100, default="Members of this group are"
    )

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("icon_classes"),
        FieldPanel("members_label"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("icon_classes"),
        APIField("members_label"),
        APIField("councillors", serializer=RelatedPersonPageListSerializer()),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]

    @property
    def councillors_count(self):
        return self.councillors.count()


class AdministratorPage(PersonPage):
    subpage_types = []


class AdministrationIndexPage(Page):
    subpage_types = [
        "core.AdministratorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)
    icon_classes = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("icon_classes"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("icon_classes"),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages",
            serializer=RelatedPersonPageListSerializer(source="get_children.live"),
        ),
    ]


class PoliticalRepsIndexPage(Page):
    subpage_types = [
        "core.CouncillorGroupPage",
        "core.CouncillorListPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)
    icon_classes = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("icon_classes"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("icon_classes"),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages",
            serializer=RelatedCouncillorGroupPageSerializer(source="get_children.live"),
        ),
    ]


class ServicePointPage(Page):
    subpage_types = []

    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    office_hours = RichTextField(features=NON_LINK_FEATURES, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("office_hours"),
        InlinePanel("service_point_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("office_hours"),
        APIField("service_point_contacts", serializer=ContactSerializer(many=True)),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class ServicePage(Page):
    subpage_types = ["core.ServicePointPage"]

    icon_classes = models.CharField(max_length=250)
    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    office_hours = RichTextField(features=NON_LINK_FEATURES, blank=True)
    head_of_service = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        FieldPanel("overview"),
        FieldPanel("office_hours"),
        PageChooserPanel("head_of_service", "core.AdministratorPage"),
        InlinePanel("service_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField("overview"),
        APIField("office_hours"),
        APIField("head_of_service", serializer=RelatedPersonPageSerializer()),
        APIField("service_contacts", serializer=ContactSerializer(many=True)),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class MyMuniPage(Page):
    subpage_types = [
        "core.PoliticalRepsIndexPage",
        "core.AdministrationIndexPage",
        "core.NoticeIndexPage",
        "core.NewsIndexPage",
        "core.ContactsPage",
        "core.RedirectorPage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class ServicesIndexPage(Page):
    subpage_types = [
        "core.ServicePage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class HomePage(Page):
    subpage_types = [
        "core.ServicesIndexPage",
        "core.MyMuniPage",
        "core.PrivacyPolicyPage"
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class NoticeIndexPage(Page):
    subpage_types = [
        "core.NoticePage",
    ]

    max_count_per_parent = 1

    icon_classes = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages",
            serializer=RelatedNoticePagesSerializer(source="get_children.live"),
        ),
    ]


class NoticePage(Page):
    subpage_types = []

    body = RichTextField(features=NON_EMBEDS_FEATURES)
    featured = models.BooleanField(default=False)
    subtitle = models.CharField(max_length=512, default="")

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("featured"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("featured"),
        APIField("body"),
        APIField("body_html", serializer=RichTextFieldSerializer(source="body")),
        APIField(
            "publication_date", serializer=DateTimeField(source="last_published_at")
        ),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class NewsIndexPage(Page):
    subpage_types = [
        "core.NewsPage",
    ]

    max_count_per_parent = 1

    icon_classes = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages",
            serializer=RelatedNoticePagesSerializer(source="get_children.live"),
        ),
    ]


class NewsPage(Page):
    subpage_types = []

    body = RichTextField(features=NON_EMBEDS_FEATURES)
    featured = models.BooleanField(default=False)
    subtitle = models.CharField(max_length=512, default="")

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("featured"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("featured"),
        APIField("body"),
        APIField("body_html", serializer=APIRichTextSerializer(source="body")),
        APIField(
            "publication_date", serializer=DateTimeField(source="last_published_at")
        ),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class ContactsPage(Page):
    subpage_types = []

    icon_classes = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        InlinePanel("emergency_contacts", label="Emergency Contacts"),
        InlinePanel(
            "provincial_government_contacts", label="Provincial Government Contacts"
        ),
        InlinePanel(
            "national_government_contacts", label="National Government Contacts"
        ),
    ]

    max_count_per_parent = 1

    api_fields = [
        APIField("icon_classes"),
        APIField("emergency_contacts", serializer=KeyContactSerializer(many=True)),
        APIField(
            "provincial_government_contacts", serializer=KeyContactSerializer(many=True)
        ),
        APIField(
            "national_government_contacts", serializer=KeyContactSerializer(many=True)
        ),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]


class ServiceRequest(models.Model):
    """ Service Request as defined by the Collaborator Web API template object (id=9) """

    QUEUED = "queued"
    CREATED = "created"
    ASSIGNED = "assigned"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (QUEUED, "Queued"),
        (CREATED, "Created"),
        (ASSIGNED, "Assigned"),
        (COMPLETED, "Completed"),
    )

    COLLABORATOR_INITIAL = "initial"
    COLLABORATOR_REGISTERED = "registered"
    COLLABORATOR_ASSIGNED = "assigned"
    COLLABORATOR_COMPLETED = "completed"
    COLLABORATOR_FINALISED = "finalised"

    COLLABORATOR_STATUS_CHOICES = (
        (COLLABORATOR_INITIAL, "Initial"),
        (COLLABORATOR_REGISTERED, "Registered"),
        (COLLABORATOR_ASSIGNED, "Assigned"),
        (COLLABORATOR_COMPLETED, "Completed"),
        (COLLABORATOR_FINALISED, "Finalised"),
    )

    collaborator_object_id = models.PositiveIntegerField(
        help_text="The Object ID for this object in the Collaborator Web API",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=254, blank=True, null=True)
    user_name = models.CharField(max_length=254, blank=True, null=True)
    user_surname = models.CharField(max_length=254, blank=True, null=True)
    user_mobile_number = models.CharField(max_length=30, blank=True, null=True)
    user_email_address = models.EmailField(max_length=254, blank=True, null=True)
    municipal_account_number = models.CharField(max_length=254, blank=True, null=True)
    street_name = models.CharField(max_length=254, blank=True, null=True)
    street_number = models.CharField(max_length=254, blank=True, null=True)
    suburb = models.CharField(max_length=254, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    coordinates = models.CharField(max_length=254, blank=True, null=True)
    request_date = models.DateTimeField(default=None, blank=True, null=True)
    on_premis_reference = models.CharField(max_length=254, blank=True, null=True)
    collaborator_status = models.CharField(
        max_length=254,
        choices=COLLABORATOR_STATUS_CHOICES,
        default=None,
        blank=True,
        null=True,
    )
    status = models.CharField(max_length=254, choices=STATUS_CHOICES, default=QUEUED)
    demarcation_code = models.CharField(max_length=254, blank=True, null=True)

    def set_status(self) -> None:
        """ Set 'status' based on 'collaborator_status' and 'on_premis_reference' values. """
        is_initial_or_registered = (
            self.collaborator_status == self.COLLABORATOR_INITIAL
            or self.collaborator_status == self.COLLABORATOR_REGISTERED
        )

        is_assigned = self.collaborator_status == self.COLLABORATOR_ASSIGNED

        is_completed_or_finalised = (
            self.collaborator_status == self.COLLABORATOR_COMPLETED
            or self.collaborator_status == self.COLLABORATOR_FINALISED
        )

        if not self.collaborator_status:
            self.status = self.QUEUED
        elif is_initial_or_registered:
            self.status = self.CREATED
        elif is_assigned and self.on_premis_reference:
            self.status = self.ASSIGNED
        elif is_completed_or_finalised and self.on_premis_reference:
            self.status = self.COMPLETED
        else:
            # Fail loudly so that we're certain that we've mapped all possible states correctly.
            raise ValueError(
                f"Not able to map collaborator status to local status. "
                f"'Collaborator status' == '{self.collaborator_status}' and "
                f"'On Premis Reference' == '{self.on_premis_reference}'"
            )


class RedirectorPage(Page):
    """
    https://www.yellowduck.be/posts/creating-redirector-page-wagtail/
    """

    icon_classes = models.CharField(max_length=100, blank=True)
    redirect_to = models.CharField(
        max_length=500, help_text="The URL to redirect to", blank=False,
    )

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        FieldPanel("redirect_to", classname="full"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField("redirect_to"),
    ]

    def get_admin_display_title(self):
        return format_html(f"{self.draft_title}<br/>{self.redirect_to}")

    class Meta:
        verbose_name = "Redirector"

    def get_url(self, request=None, current_site=None):
        return self.redirect_to

    def get_full_url(self, request=None, current_site=None):
        return self.redirect_to

    def serve(self, request):
        return redirect(self.redirect_to)


def service_request_attachment_file_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"service-requests/{instance.service_request.id}/attachments/{uuid.uuid4()}.{extension}/"


class ServiceRequestAttachment(models.Model):
    """ Attachment for a Service Request object """

    service_request = models.ForeignKey(
        to=ServiceRequest, on_delete=models.CASCADE, related_name="images"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=service_request_attachment_file_path)
    content_type = models.CharField(max_length=255)
    exists_on_collaborator = models.BooleanField(default=False)


class PrivacyPolicyPage(Page):
    subpage_types = []
    max_count_per_parent = 1

    body = RichTextField(features=NON_EMBEDS_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("body"),
        APIField("body_html", serializer=APIRichTextSerializer(source="body")),
        APIField(
            "publication_date", serializer=DateTimeField(source="last_published_at")
        ),
        APIField(
            "ancestor_pages",
            serializer=RelatedPagesSerializer(source="get_ancestors.live"),
        ),
        APIField(
            "child_pages", serializer=RelatedPagesSerializer(source="get_children.live")
        ),
    ]
