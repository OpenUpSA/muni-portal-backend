from datetime import datetime
from muni_portal.core.models import ServiceRequest, ServiceRequestImage
from rest_framework import serializers
from muni_portal.collaborator_api.types import ServiceRequestObject


class ServiceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRequest
        fields = '__all__'

    def update(self, instance: ServiceRequest, validated_data: ServiceRequestObject):
        """ Update a local object instance with a remote object instance. """

        # Parse ISO datetime format (default to instance value if not present)
        request_date = instance.request_date
        request_date_iso_fmt = validated_data.get("F12", None)
        if request_date_iso_fmt:
            request_date = datetime.fromisoformat(request_date_iso_fmt)

        instance.type = validated_data.get("F1", instance.type)
        instance.user_name = validated_data.get("F2", instance.user_name)
        instance.user_surname = validated_data.get("F3", instance.user_surname)
        instance.user_mobile_number = validated_data.get("F4", instance.user_mobile_number)
        instance.user_email_address = validated_data.get("F5", instance.user_email_address)
        instance.municipal_account_number = validated_data.get("F6", instance.municipal_account_number)
        instance.street_name = validated_data.get("F7", instance.street_name)
        instance.street_number = validated_data.get("F8", instance.street_number)
        instance.suburb = validated_data.get("F9", instance.suburb)
        instance.description = validated_data.get("F10", instance.description)
        instance.coordinates = validated_data.get("F11", instance.coordinates)
        instance.request_date = request_date
        instance.on_premis_reference = validated_data.get("F14", instance.on_premis_reference)
        instance.collaborator_status = validated_data.get("F15", instance.collaborator_status).lower()
        instance.demarcation_code = validated_data.get("F20", instance.demarcation_code)

        instance.set_status()
        instance.save()

        return instance


class ServiceRequestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestImage
        fields = ('id', 'file', 'date_created', 'exists_on_collaborator')
