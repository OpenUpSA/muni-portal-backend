from django.contrib.auth.models import User
from django.http import Http404
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views
from typing import List, Union

from muni_portal.collaborator_api.client import Client
from muni_portal.collaborator_api.types import FormField
from muni_portal.core.django_q_tasks import create_service_request, create_attachment
from muni_portal.core.django_q_hooks import handle_service_request_create, handle_service_request_image_create
from muni_portal.core.models import ServiceRequest, ServiceRequestImage
from muni_portal.core.model_serializers import ServiceRequestSerializer, ServiceRequestImageSerializer
from django.conf import settings
from django_q.tasks import async_task


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

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: int) -> Response:
        local_object = self.get_object(pk, request.user)
        object_id = local_object.collaborator_object_id
        serializer = ServiceRequestSerializer(local_object)

        if not object_id:
            # Object does not exist in collaborator yet, so return local object without updating from collaborator
            return Response(serializer.data)

        client = Client(
            settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD
        )
        client.authenticate()
        remote_object = client.get_task(object_id)
        serializer.update(local_object, remote_object)
        return Response(serializer.data)


class ServiceRequestListCreateView(ServiceRequestAPIView):
    permission_classes = [IsAuthenticated]

    CREATE_REQUIRED_FIELDS = (
        "type",
        "user_name",
        "user_surname",
        "user_mobile_number",
        "street_name",
        "street_number",
        "suburb",
        "description",
    )

    def get(self, request: Request) -> Response:
        """
        Return list of ServiceRequest objects.

        We build the list by retrieving all local ServiceRequest objects for this user and requesting a detail view
        of each object from Collaborator Web API and returning it as a list.
        """
        response_list = []
        local_objects_with_ids = ServiceRequest.objects.filter(
            user=request.user, collaborator_object_id__isnull=False
        )
        local_objects_without_ids = ServiceRequest.objects.filter(
            user=request.user, collaborator_object_id__isnull=True
        )

        if local_objects_with_ids:
            client = Client(
                settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD
            )
            client.authenticate()

            for service_request in local_objects_with_ids:
                local_object = self.get_object(service_request.pk, request.user)
                serializer = ServiceRequestSerializer(local_object)
                remote_object = client.get_task(local_object.collaborator_object_id)
                serializer.update(local_object, remote_object)
                response_list.append(serializer.data)

        for local_object in local_objects_without_ids:
            serializer = ServiceRequestSerializer(local_object)
            response_list.append(serializer.data)

        return Response(response_list)

    def post(self, request: Request) -> Response:
        """
        Create a new Service Request object.

        The object will first be created in Collaborator Web API, and if successful,
        it will be created in this API.
        """
        # Return error if any of the fields are missing
        received_fields = request.data.keys()
        missing_fields = []
        for field in self.CREATE_REQUIRED_FIELDS:
            if field not in received_fields:
                missing_fields.append(field)
        if missing_fields:
            error_response_dict = {}
            for field in missing_fields:
                error_response_dict[field] = "This field is required."
            return Response(error_response_dict, status=400)

        request_type = request.data.get("type")
        user_name = request.data.get("user_name")
        user_surname = request.data.get("user_surname")
        user_mobile_number = request.data.get("user_mobile_number")
        user_email_address = request.data.get("user_email_address")
        street_name = request.data.get("street_name")
        street_number = request.data.get("street_number")
        suburb = request.data.get("suburb")
        description = request.data.get("description")
        coordinates = request.data.get("coordinates")

        request_date = timezone.now()
        request_date_iso = request_date.isoformat()
        demarcation_code = "WC033"

        serializer = ServiceRequestSerializer(
            data={
                "user": request.user.pk,
                "type": request_type,
                "user_name": user_name,
                "user_surname": user_surname,
                "user_mobile_number": user_mobile_number,
                "user_email_address": user_email_address,
                "street_name": street_name,
                "street_number": street_number,
                "suburb": suburb,
                "description": description,
                "coordinates": coordinates,
                "request_date": request_date,
                "demarcartion_code": demarcation_code,
            }
        )
        serializer.is_valid(raise_exception=True)

        # Translate POST parameters received into Collaborator Web API form fields
        form_fields: List[FormField] = [
            {"FieldID": "F1", "FieldValue": request_type},
            {"FieldID": "F2", "FieldValue": user_name},
            {"FieldID": "F3", "FieldValue": user_surname},
            {"FieldID": "F4", "FieldValue": user_mobile_number},
            {"FieldID": "F5", "FieldValue": user_email_address},
            {"FieldID": "F7", "FieldValue": street_name},
            {"FieldID": "F8", "FieldValue": street_number},
            {"FieldID": "F9", "FieldValue": suburb},
            {"FieldID": "F10", "FieldValue": description},
            {"FieldID": "F11", "FieldValue": coordinates},
            {"FieldID": "F12", "FieldValue": request_date_iso},
            {"FieldID": "F20", "FieldValue": demarcation_code},
        ]

        service_request = ServiceRequest.objects.create(
            user=request.user,
            type=request_type,
            request_date=request_date,
            user_name=user_name,
            user_surname=user_surname,
            user_mobile_number=user_mobile_number,
            user_email_address=user_email_address,
            street_name=street_name,
            street_number=street_number,
            suburb=suburb,
            description=description,
            coordinates=coordinates,
            demarcation_code=demarcation_code,
        )

        async_task(
            create_service_request,
            service_request.id,
            form_fields,
            hook=handle_service_request_create,
        )

        return Response(status=201)


class ServiceRequestImageListCreateView(views.APIView):
    """
    This API View supports listing the images for a service request and creating images for an existing service
    request.

    It does not support creating images with a new service request, instead that is handled on the
    Service Request create view.
    """
    # permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def get_service_request(service_request_pk: int, user: User) -> Union[ServiceRequest, Response]:
        try:
            return ServiceRequest.objects.get(pk=service_request_pk, user=user)
        except ServiceRequest.DoesNotExist:
            return Response(status=404)

    def get(self, request: Request, service_request_pk: int) -> Response:
        """ Return a list of images for a specific Service Request object """
        service_request = self.get_service_request(service_request_pk, User.objects.first())  # TODO: set to request
        if type(service_request) == Response:
            return service_request

        images = ServiceRequestImageSerializer(service_request.images.all(), many=True)

        return Response(images.data)

    def post(self, request: Request, service_request_pk: int) -> Response:
        """ Create an image attachment for an existing Service Request object """
        service_request = self.get_service_request(service_request_pk, User.objects.first())  # TODO: set to request
        if type(service_request) == Response:
            return service_request

        serializer = ServiceRequestImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.save(
                service_request=service_request,
                file=request.data.get('file')
            )

            # If the service request object doesn't have an ID yet it'll execute the async task after it has received
            # an ID in django_q_hooks.py
            if service_request.collaborator_object_id:
                async_task(
                    create_attachment,
                    image.id,
                    hook=handle_service_request_image_create
                )
            return Response(status=201)
        else:
            return Response(serializer.errors, status=400)
