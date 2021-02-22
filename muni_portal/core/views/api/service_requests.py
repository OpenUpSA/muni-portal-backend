from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from muni_portal.collaborator_api.client import Client
from muni_portal.core.models import ServiceRequest
from muni_portal.core.model_serializers import ServiceRequestSerializer
from django.conf import settings


class ServiceRequestApiView(APIView):

    def get_object(self, pk: int):
        try:
            return ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        local_object = self.get_object(pk)
        object_id = local_object.collaborator_object_id

        print(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
        client.authenticate()
        remote_object = client.get_task(object_id)

        # serializer = ServiceRequestSerializer(local_object, data=remote_object)

        # return Response(serializer.data)
        return Response(remote_object)
