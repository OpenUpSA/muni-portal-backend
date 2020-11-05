from django.views import generic
from rest_framework import serializers, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from muni_portal.core.models import Webhook


class Index(generic.TemplateView):
    template_name = "index.html"


class WebhooksView(CreateAPIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    def create(self, request, *args, **kwargs):
        try:
            Webhook.objects.create(data=request.data)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": e})
