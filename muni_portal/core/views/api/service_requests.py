from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins, views
from muni_portal.collaborator_api.client import Client
from muni_portal.core.models import ServiceRequest
from muni_portal.core.model_serializers import ServiceRequestSerializer
from django.conf import settings


class ServiceRequestDetailView(views.APIView):
    """
    Return detail of ServiceRequest object.

    First fetches from Collaborator Web API, then updates local instance with remote instance (if found), then
    returns local instance.
    """

    # TODO: uncomment this (how is settings done currently?)
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def get_object(pk: int) -> ServiceRequest:
        try:
            return ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk: int) -> Response:
        local_object = self.get_object(pk)
        object_id = local_object.collaborator_object_id
        serializer = ServiceRequestSerializer(local_object)

        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()
        remote_object = client.get_task(object_id)
        serializer.update(local_object, remote_object)
        return Response(serializer.data)


class ServiceRequestListView(views.APIView):
    """
    Return list of ServiceRequest objects.

    We build the list by retrieving all local ServiceRequest objects for this user and requesting a detail view
    of each object from Collaborator Web API and returning it as a list.
    """

    @staticmethod
    def get_object(pk: int) -> ServiceRequest:
        try:
            return ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request) -> Response:
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
            local_object = self.get_object(service_request.pk)
            serializer = ServiceRequestSerializer(local_object)
            remote_object = client.get_task(local_object.collaborator_object_id)
            serializer.update(local_object, remote_object)
            response_list.append(serializer.data)

        return Response(response_list)
