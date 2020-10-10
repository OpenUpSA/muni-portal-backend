from rest_framework import serializers
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
