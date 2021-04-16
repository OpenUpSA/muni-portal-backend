from django_q.tasks import AsyncTask, async_task

from muni_portal.core.django_q_tasks import create_attachment
from muni_portal.core.models import ServiceRequest, ServiceRequestImage


def handle_service_request_create(task: AsyncTask) -> None:
    """
    Handle the response received after a Service Request object is synced
    to Collaborator Web API
    """
    response, service_request_id = task.result
    collaborator_object_id = response.json().get("Data").get("ObjID")

    service_request = ServiceRequest.objects.get(id=service_request_id)
    service_request.collaborator_object_id = collaborator_object_id
    service_request.save()
    print('Service request updated with collaborator_object_id from response.')

    # There may be images waiting to be created
    for image in service_request.images.filter(exists_on_collaborator=False):
        async_task(
            create_attachment,
            image.id,
            hook=handle_service_request_image_create
        )


def handle_service_request_image_create(task: AsyncTask) -> None:
    """
    Handle the response received after a Service Request Image object is synced to
    Collaborator Web API
    """
    response, service_request_image_id = task.result

    service_request_image = ServiceRequestImage.objects.get(id=service_request_image_id)
    service_request_image.exists_on_collaborator = True
    service_request_image.save()
    print('Service request image updated with exists_on_collaborator=True.')
