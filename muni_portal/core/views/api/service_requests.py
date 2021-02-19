from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from muni_portal.core.models import ServiceRequest


@require_http_methods(["GET"])
def service_request_detail(request) -> None:
    """ Service Request detail view """


class ServiceRequestApiView(APIView):

    def get_object(self, pk: int):
        try:
            ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        service_request = self.get_object(pk)
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data)
