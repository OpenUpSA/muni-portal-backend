from typing import List
from muni_portal.collaborator_api.client import Client
from django.conf import settings
from muni_portal.collaborator_api.types import FormField
from requests import Response


def create_service_request(service_request_id: int, form_fields: List[FormField]) -> (Response, int):
    """
    Create a Service Request with the Collaborator Web API endpoint.

    We pass service_request_id on so that the receiving hook knows which Service Request object we're working with.
    """
    client = Client(settings.COLLABORATOR_API_USERNAME, settings.COLLABORATOR_API_PASSWORD)
    client.authenticate()
    response = client.create_task(form_fields)
    return response, service_request_id
