from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views
from typing import List

from muni_portal.collaborator_api.client import Client
from muni_portal.collaborator_api.types import FormField
from muni_portal.core.models import ServiceRequest
from muni_portal.core.model_serializers import ServiceRequestSerializer
from django.conf import settings


class ServiceRequestAPIView(views.APIView):

    @staticmethod
    def get_object(pk: int, user: User) -> ServiceRequest:
        try:
            return ServiceRequest.objects.get(pk=pk, user=user)
        except ServiceRequest.DoesNotExist:
            raise Http404


class ServiceRequestDetailView(ServiceRequestAPIView):
    """
    Return detail of ServiceRequest object.

    First fetches from Collaborator Web API, then updates local instance with remote instance (if found), then
    returns local instance.
    """

    # TODO: uncomment this
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk: int) -> Response:
        # local_object = self.get_object(pk, request.user)
        # TODO: Swap bottom line for top line
        local_object = self.get_object(pk, User.objects.first())
        object_id = local_object.collaborator_object_id
        serializer = ServiceRequestSerializer(local_object)

        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()
        remote_object = client.get_task(object_id)
        serializer.update(local_object, remote_object)
        return Response(serializer.data)


class ServiceRequestListCreateView(ServiceRequestAPIView):

    # TODO: uncomment this
    # permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        """
        Return list of ServiceRequest objects.

        We build the list by retrieving all local ServiceRequest objects for this user and requesting a detail view
        of each object from Collaborator Web API and returning it as a list.
        """
        response_list = []
        # local_objects = ServiceRequest.objects.filter(user=request.user)
        # TODO: use request.user as above
        local_objects = ServiceRequest.objects.filter(user=User.objects.first())

        if local_objects:
            client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
            client.authenticate()
        else:
            return Response([])

        for service_request in local_objects:
            local_object = self.get_object(service_request.pk, User.objects.first())
            serializer = ServiceRequestSerializer(local_object)
            remote_object = client.get_task(local_object.collaborator_object_id)
            serializer.update(local_object, remote_object)
            response_list.append(serializer.data)

        return Response(response_list)

    def post(self, request) -> Response:
        """
        Create a new Service Request object.

        The object will first be created in Collaborator Web API, and if successful,
        it will be created in this API.
        """

        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()

        required_fields = (
            "user_name", "user_surname", "user_mobile_number",
            "street_name", "street_number", "suburb", "description"
        )

        # Return error if any of the fields are missing
        received_fields = request.data.keys()
        missing_fields = []
        for field in required_fields:
            if field not in received_fields:
                missing_fields.append(field)
        if missing_fields:
            error_response_dict = {}
            for field in missing_fields:
                error_response_dict[field] = "This field is required."
            return Response(error_response_dict, status=400)

        # Translate POST parameters received into Collaborator Web API form fields
        form_fields: List[FormField] = [
            {"FieldID": "F2", "FieldValue": request.data.get("user_name")},
            {"FieldID": "F3", "FieldValue": request.data.get("user_surname")},
            {"FieldID": "F4", "FieldValue": request.data.get("user_mobile_number")},
            {"FieldID": "F5", "FieldValue": request.user.email},
            {"FieldID": "F7", "FieldValue": request.data.get("street_name")},
            {"FieldID": "F8", "FieldValue": request.data.get("street_number")},
            {"FieldID": "F9", "FieldValue": request.data.get("suburb")},
            {"FieldID": "F10", "FieldValue": request.data.get("description")},
            {"FieldID": "F11", "FieldValue": request.data.get("coordinates")},
        ]

        response = client.create_task(form_fields)
        print('RESPONSE BELOW')
        print(response)
        print('RESPONSE JSON BELOW')
        print(response.json())

        return Response(request.data)
