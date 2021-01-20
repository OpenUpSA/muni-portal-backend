import logging

from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from muni_portal.core.models import Webhook

logger = logging.getLogger(__name__)


class BearerApiKeyTokenAuthentication(TokenAuthentication):
    """
    This uses the TokenAuthentication backend, but more in the sense of
    an API Key that doesn't change frequently - only when compromised or
    for regular manual cycling of keys.
    Collabrator currently wants to provide the keyword "Bearer" before
    the token since they have been doing temporary bearer token integrations.
    """
    keyword = "Bearer"


class CollaboratorWebhookApiView(CreateAPIView):
    authentication_classes = [BearerApiKeyTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    def create(self, request, *args, **kwargs):
        Webhook.objects.create(data=request.data)
        return Response(status=status.HTTP_201_CREATED)
