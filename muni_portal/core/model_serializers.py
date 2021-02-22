from muni_portal.core.models import ServiceRequest
from rest_framework import serializers
from muni_portal.collaborator_api.types import ServiceRequestObject


class ServiceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRequest
        fields = '__all__'

    def update(self, instance, validated_data: ServiceRequestObject):

        # obj_id = validated_data.get("obj_id", None)
        # template_id = validated_data.get("template_id", None)
        # f0 = validated_data.get("F0", None)
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
        instance.request_date = validated_data.get("F12", instance.request_date)
        instance.mobile_reference = validated_data.get("F13", instance.mobile_reference)
        instance.on_premis_reference = validated_data.get("F14", instance.on_premis_reference)
        instance.status = validated_data.get("F15", instance.status)
        # f18 = validated_data.get("F18", None)
        # f19 = validated_data.get("F19", None)
        instance.demarcation_code = validated_data.get("F25", instance.demarcation_code)

        instance.save()

        return instance
