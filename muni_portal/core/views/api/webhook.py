import logging

from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from muni_portal.core.models import Webhook

logger = logging.getLogger(__name__)


class WebhooksApiView(CreateAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    def create(self, request, *args, **kwargs):
        try:
            Webhook.objects.create(data=request.data)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": e})
