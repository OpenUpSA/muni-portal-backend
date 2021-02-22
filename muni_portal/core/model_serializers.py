from muni_portal.core.models import ServiceRequest
from rest_framework import serializers
from muni_portal.collaborator_api.types import ServiceRequestObject


class ServiceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRequest
        fields = ['__all__']

    def update(self, instance, validated_data: ServiceRequestObject):

        # TODO: remove unused fields
        obj_id = validated_data.get("obj_id", None)
        template_id = validated_data.get("template_id", None)
        f0 = validated_data.get("F0", None)
        f1 = validated_data.get("F1", None)
        f2 = validated_data.get("F2", None)
        f3 = validated_data.get("F3", None)
        f4 = validated_data.get("F4", None)
        f5 = validated_data.get("F5", None)
        f6 = validated_data.get("F6", None)
        f7 = validated_data.get("F7", None)
        f8 = validated_data.get("F8", None)
        f9 = validated_data.get("F9", None)
        f10 = validated_data.get("F10", None)
        f11 = validated_data.get("F11", None)
        f12 = validated_data.get("F12", None)
        f13 = validated_data.get("F13", None)
        f14 = validated_data.get("F14", None)
        f15 = validated_data.get("F15", None)
        f18 = validated_data.get("F18", None)
        f19 = validated_data.get("F19", None)
        f25 = validated_data.get("F25", None)

        if f1:
            instance.type = f1
        if f2:
            instance.user_name = f2
        if f3:
            instance.user_surname = f3
        if f4:
            instance.user_mobile_number = f4
        if f5:
            instance.user_email_address = f5
        if f6:
            instance.municipal_account_number = f6
        if f7:
            instance.street_name = f7
        if f8:
            instance_street_number = f8
        if f9:
            instance.suburb = f9
        if f10:
            instance.description = f10
        if f11:
            instance.coordinates = f11
        if f12:
            # TODO: convert to date object before saving to instance
            instance.request_date = f12
        if f13:
            instance.mobile_reference = f13
        if f14:
            instance.on_premis_reference = f14
        if f15:
            instance.status = f15
        if f25:
            instance.demarcation_code = f25

        instance.save()

        return instance
