from typing import List
from muni_portal.collaborator_api.client import Client
from django.conf import settings
from muni_portal.collaborator_api.types import FormField
from requests import Response

from muni_portal.core.models import ServiceRequestAttachment


def create_service_request(
    service_request_id: int, form_fields: List[FormField]
) -> (Response, int):
    """
    Create a Service Request with the Collaborator Web API endpoint.
    """
    client = Client(
        settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD
    )
    client.authenticate()
    response = client.create_task(form_fields)
    return response, service_request_id


def create_attachment(service_request_image_id: int) -> (Response, int):
    """
    Create an Attachment from an existing ServiceRequestAttachment object with the Collaborator Web API endpoint.
    """
    client = Client(
        settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD
    )
    client.authenticate()

    service_request_image = ServiceRequestAttachment.objects.get(
        id=service_request_image_id
    )

    if not service_request_image.service_request.collaborator_object_id:
        raise AssertionError(
            "Service Request must have an object_id before a ServiceRequestAttachment can be created for it"
        )

    if service_request_image.exists_on_collaborator:
        raise AssertionError("Service Request Image already exists on Collaborator")

    response = client.create_attachment(
        service_request_image.service_request.collaborator_object_id,
        service_request_image.file,
        service_request_image.content_type,
    )
    return response, service_request_image_id
