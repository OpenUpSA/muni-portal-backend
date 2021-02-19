from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from muni_portal.collaborator_api.client import Client
from muni_portal.core.models import ServiceRequest
from muni_portal.core.serializers import ServiceRequestSerializer
from django.conf import settings


class ServiceRequestApiView(APIView):

    def get_object(self, pk: int):
        try:
            ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        local_service_request = self.get_object(pk)
        object_id = local_service_request.object_id

        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()
        remote_service_request = client.get_task(object_id)

        # TODO: Update local object with fetched object (probably using serializer)

        serializer = ServiceRequestSerializer(local_service_request)
        return Response(serializer.data)
