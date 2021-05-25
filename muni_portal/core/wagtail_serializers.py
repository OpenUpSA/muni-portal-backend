from rest_framework import serializers, fields
from rest_framework.fields import Field
from wagtail.core.rich_text import expand_db_html
from wagtail.core.templatetags import wagtailcore_tags
from wagtail.images.api.fields import ImageRenditionField


class APIRichTextSerializer(fields.CharField):
    """ https://github.com/wagtail/wagtail/issues/2695#issuecomment-373002412 """
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return expand_db_html(representation)


class SerializerMethodNestedSerializer(serializers.SerializerMethodField):
    """
    Returns nested serializer in serializer method field
    https://stackoverflow.com/a/63676418
    """

    def __init__(self, serializer, serializer_kwargs=None, **kwargs):
        self.serializer = serializer
        self.serializer_kwargs = serializer_kwargs or {}
        super(SerializerMethodNestedSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
        repr_value = super(SerializerMethodNestedSerializer, self).to_representation(
            value
        )
        if repr_value is not None:
            return self.serializer(repr_value, **self.serializer_kwargs).data


class ImageSerializerField(Field):
    """A custom serializer for image field."""

    def to_representation(self, value):
        return {
            "url": value.file.url,
            "width": value.width,
            "height": value.height,
            "alt": value.title,
        }


class RelatedPagesSerializer(Field):
    @staticmethod
    def page_representation(page):
        return {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "url": page.url,
            "icon_classes": page.icon_classes
            if hasattr(page, "icon_classes")
            else None,
        }

    def to_representation(self, pages):
        return [self.page_representation(page) for page in pages.specific()]


class RelatedCouncillorGroupPageSerializer(RelatedPagesSerializer):
    def page_representation(self, page):
        representation = super().page_representation(page)
        representation["councillors_count"] = (
            page.councillors_count if hasattr(page, "councillors_count") else None
        )
        return representation


class RelatedPersonPageSerializer(Field):
    """A custom serializer for related PersonPage."""

    read_only = True
    write_only = False

    @staticmethod
    def get_representation(value):
        return {
            "id": value.id,
            "title": value.title,
            "slug": value.slug,
            "url": value.url,
            "icon_classes": value.icon_classes
            if hasattr(value, "icon_classes")
            else None,
            "profile_image": None,
            "profile_image_thumbnail": None,
            "job_title": None,
        }

    def to_representation(self, value):
        result = self.get_representation(value)
        if value.specific.profile_image:
            result["profile_image"] = ImageSerializerField().to_representation(
                value.specific.profile_image
            )
            result["profile_image_thumbnail"] = ImageRenditionField(
                "max-100x100"
            ).to_representation(value.specific.profile_image)
        if value.specific.job_title:
            result["job_title"] = value.specific.job_title
        return result


class RelatedPersonPageListSerializer(RelatedPersonPageSerializer):
    def to_representation(self, pages):
        pages = pages if pages is list else pages.all()
        return [
            super(RelatedPersonPageListSerializer, self).to_representation(page)
            for page in pages
        ]


class WebpushSubscriptionSerializer(serializers.Serializer):
    subscription_object = serializers.DictField(allow_empty=False)


class RichTextFieldSerializer(Field):
    def to_representation(self, value):
        return wagtailcore_tags.richtext(value)


class RelatedNoticePagesSerializer(RelatedPagesSerializer):
    @staticmethod
    def page_representation(page):
        return {
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "publication_date": page.last_published_at,
        }

    def to_representation(self, pages):
        return [
            self.page_representation(page)
            for page in pages.order_by("-last_published_at").specific()
        ]
