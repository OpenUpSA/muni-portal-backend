from muni_portal.core.models import ServiceRequest
from rest_framework import serializers


class ServiceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRequest
        fields = ['__all__']
