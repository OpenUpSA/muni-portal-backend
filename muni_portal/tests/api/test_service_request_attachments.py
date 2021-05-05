from io import BytesIO
from unittest import mock

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django_q.tasks import async_task
from faker import Faker
from requests import Session
from rest_framework import status
from rest_framework.test import APITestCase

from muni_portal.core.django_q_hooks import handle_service_request_create
from muni_portal.core.django_q_tasks import create_service_request
from muni_portal.core.models import ServiceRequest, ServiceRequestAttachment


MOCK_CREATE_TASK_RESPONSE_JSON = {
    "Code": 0,
    "Message": "Success",
    "DetailedMessages": None,
    "CollaboratorUri": "https://consumercollab.collaboratoronline.com/collab/",
    "Data": {
        "obj_id": 1,
        "template_id": 9,
        "F0": "",
        "F1": "Sewerage",
        "F2": "Mr JD",
        "F3": "Bothma",
        "F4": "0792816737",
        "F5": "jd@openup.org.za",
        "F7": "Geen Straat",
        "F8": "123",
        "F9": "Daar",
        "F10": "This one has the date 2020-02-01 sent from the app",
        "F11": "12.3, 45.6",
        "F12": "2020-02-01",
        "F14": "373761",
        "F15": "Assigned",
        "F18": "Mr Bothma. Cape Agulhas Municipality confirms receipt of your request. Ref No 373761",
        "F19": "556704",
        "F20": "WC033",
    },
}


@override_settings(DJANGO_Q_SYNC=True)
class ApiServiceRequestAttachmentsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = Faker().password(length=8)
        cls.user = User.objects.create_user(
            username="test", email="test@test.com", password=cls.password
        )
        cls.service_request_one = ServiceRequest.objects.create(
            collaborator_object_id=1, user=cls.user
        )
        cls.attachment_one = ServiceRequestAttachment.objects.create(
            service_request=cls.service_request_one,
            file=cls.generate_fake_file(),
            content_type="image/png",
        )

    def authenticate(self) -> None:
        data = {"username": self.user.username, "password": self.password}
        response = self.client.post(reverse("token_obtain_pair"), data=data)
        jwt_token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")

    @staticmethod
    def get_mock_auth_response() -> mock.Mock:
        mock_auth_response = mock.Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = "testToken"
        return mock_auth_response

    @staticmethod
    def get_mock_create_response() -> mock.Mock:
        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_CREATE_TASK_RESPONSE_JSON
        return mock_detail_response

    @staticmethod
    def generate_fake_file() -> SimpleUploadedFile:
        return SimpleUploadedFile(
            "test.jpg", b"fake bytes file content", content_type="image/jpg"
        )

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_get_list(self, mock_post):
        """ Test GET list view returns correct schema and values """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        response = self.client.get(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            )
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected_response_data = {
            "id": self.attachment_one.id,
            "file": settings.MEDIA_URL + self.attachment_one.file.name,
            "date_created": self.attachment_one.date_created.isoformat()[:-6] + "Z",
            "exists_on_collaborator": False,
        }

        self.assertDictEqual(dict(response.data[0]), expected_response_data)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_get_detail(self, mock_post):
        """ Test GET detail view returns bytes with correct content type """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        response = self.client.get(
            reverse(
                "service-request-attachment-detail",
                kwargs={
                    "service_request_pk": self.service_request_one.pk,
                    "service_request_image_pk": self.attachment_one.pk,
                },
            )
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response["Content-Type"], self.attachment_one.content_type)
        self.assertEquals(type(response.content), bytes)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_one_attachment_for_existing_service_request(self, mock_post):
        """
        Test creating a single attachment in one request for an existing service request object
        """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        ServiceRequestAttachment.objects.all().delete()
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 0)

        data = {"files": (self.generate_fake_file(),)}

        response = self.client.post(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            ),
            data=data,
            format="multipart",
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 1)

        # It should have been synced to collaborator since the object already exists
        self.assertTrue(ServiceRequestAttachment.objects.first().exists_on_collaborator)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_multiple_attachments_for_existing_service_request(self, mock_post):
        """
        Test creating multiple attachments in one request for an existing service request object
        """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        ServiceRequestAttachment.objects.all().delete()
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 0)

        data = {"files": (self.generate_fake_file(),) * 3}

        response = self.client.post(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            ),
            data=data,
            format="multipart",
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 3)

        for attachment in ServiceRequestAttachment.objects.all():
            self.assertTrue(attachment.exists_on_collaborator)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_fail_missing_files(self, mock_post):
        """
        Test that the correct failure is returned if no files are present in the request
        """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        response = self.client.post(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            ),
            format="multipart",
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, "post")
    def test_create_attachment_before_object_id_returned(self, mock_post, mock_session_post):
        """
        Test creating an attachment for a service request object that does not yet have an object id.

        1. The Service Request Attachment object should be created but not yet queued for creation in collaborator,
        2. then the Service Request object must be created on collaborator and have an object id assigned to it,
        3. then the attachment should be created in collaborator by the service request created hook.
        """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_create_response()
        self.authenticate()

        ServiceRequestAttachment.objects.all().delete()
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 0)

        self.service_request_one.collaborator_object_id = None
        self.service_request_one.save()
        self.assertIsNone(self.service_request_one.collaborator_object_id)

        data = {"files": (self.generate_fake_file(),)}

        response = self.client.post(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            ),
            data=data,
            format="multipart",
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(ServiceRequestAttachment.objects.all().count(), 1)

        # It must not have been synced to collaborator yet since the service request does not yet have an object id
        self.assertFalse(ServiceRequestAttachment.objects.first().exists_on_collaborator)

        async_task(
            create_service_request,
            self.service_request_one.id,
            [],
            hook=handle_service_request_create,
        )

        # Now it should be synced since it should have been triggered for syncing after the service request was created
        self.assertTrue(ServiceRequestAttachment.objects.first().exists_on_collaborator)
