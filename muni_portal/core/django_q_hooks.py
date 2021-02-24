from django_q.tasks import AsyncTask
from muni_portal.core.models import ServiceRequest


def handle_service_request_create(task: AsyncTask) -> None:
    """
    Handle the response received after a Service Request object is created
    on Collaborator Web API
    """
    print('Received task result!')
    response, service_request_id = task.result
    collaborator_object_id = response.json().get("Data").get("ObjID")

    service_request = ServiceRequest.objects.get(id=service_request_id)
    service_request.collaborator_object_id = collaborator_object_id
    service_request.save()
    print('Service request updated with collaborator_object_id from response.')
