from rest_framework import serializers
from rest_framework.fields import Field
from wagtail.images.api.fields import ImageRenditionField
from . import models


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
        repr_value = super(SerializerMethodNestedSerializer, self).to_representation(value)
        if repr_value is not None:
            return self.serializer(repr_value, **self.serializer_kwargs).data


class ImageSerializerField(Field):
    """A custom serializer for image field."""

    def to_representation(self, value):
        return {
            "url": value.file.url,
            "width": value.width,
            "height": value.height,
            "alt": value.title
        }


class AdministratorPageSerializer(Field):
    """A custom serializer for AdministratorPage."""

    read_only = True
    write_only = False

    def to_representation(self, value):
        if value.head_of_service and value.head_of_service.specific.profile_image:
            profile_image = ImageSerializerField().to_representation(
                value.head_of_service.specific.profile_image
            )
            profile_image_thumbnail = ImageRenditionField("max-100x100").to_representation(
                value.head_of_service.specific.profile_image
            )
            return {
                "id": value.head_of_service.specific.id,
                "title": value.head_of_service.specific.title,
                "job_title": value.head_of_service.specific.job_title,
                "profile_image": profile_image,
                "profile_image_thumbnail": profile_image_thumbnail,
            }
