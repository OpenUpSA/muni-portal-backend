import logging

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from muni_portal.core.models import WebPushSubscription
from muni_portal.core.serializers import WebpushSerializer

logger = logging.getLogger(__name__)


class WebpushApiView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = WebpushSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            WebPushSubscription.objects.create(user=request.user, **serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": e})
