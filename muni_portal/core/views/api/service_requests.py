from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from muni_portal.collaborator_api.client import Client
from muni_portal.core.models import ServiceRequest
from muni_portal.core.model_serializers import ServiceRequestSerializer
from django.conf import settings


class ServiceRequestApiView(APIView):

    # TODO: perms? depends what the default is

    @staticmethod
    def get_object(pk: int):
        try:
            return ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Return detail of ServiceRequest object.

        First fetches from Collaborator Web API, then updates local instance with remote instance (if found), then
        returns local instance.
        """
        local_object = self.get_object(pk)
        object_id = local_object.collaborator_object_id
        serializer = ServiceRequestSerializer(local_object)

        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()
        remote_object = client.get_task(object_id)

        serializer.update(local_object, remote_object)
        return Response(serializer.data)

    def list(self, request):
        """
        Return list of ServiceRequest objects.

        We build the list by retrieving all local ServiceRequest objects for this user and requesting a detail view
        of each object from Collaborator Web API and returning it as a list.
        """

        local_objects = ServiceRequest.objects.filter(user=request.user)
