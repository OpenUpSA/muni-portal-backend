from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django_q.tasks import async_task
from faker import Faker
from requests import Session
from rest_framework import status
from rest_framework.test import APITestCase

from muni_portal.core.django_q_tasks import create_service_request
from muni_portal.core.models import ServiceRequest, ServiceRequestAttachment
from muni_portal.tests.api.common_mock_values import (
    MOCK_CREATE_TASK_RESPONSE_JSON,
    MOCK_AUTH_RESPONSE,
)


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
        mock_auth_response.json.return_value = MOCK_AUTH_RESPONSE
        return mock_auth_response

    @staticmethod
    def get_mock_create_response() -> mock.Mock:
        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_CREATE_TASK_RESPONSE_JSON
        return mock_detail_response

    @staticmethod
    def get_mock_create_update_record_response(object_id: int) -> mock.Mock:
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = f"{object_id}"
        return mock_response

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

    @mock.patch.object(Session, "post")
    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_one_attachment_for_existing_service_request(
        self, mock_post, mock_session_post
    ):
        """
        Test creating a single attachment in one request for an existing service request object
        """
        self.service_request_one.collaborator_object_id = 123
        self.service_request_one.save()

        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_create_update_record_response(
            self.service_request_one.collaborator_object_id
        )
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

    @mock.patch.object(Session, "post")
    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_multiple_attachments_for_existing_service_request(
        self, mock_post, mock_session_post
    ):
        """
        Test creating multiple attachments in one request for an existing service request object
        """

        self.service_request_one.collaborator_object_id = 123
        self.service_request_one.save()

        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_create_update_record_response(
            self.service_request_one.collaborator_object_id
        )
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

    @mock.patch.object(Session, "post")
    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_create_attachment_before_object_id_returned(
        self, mock_post, mock_session_post
    ):
        """
        Test creating an attachment for a service request object that does not yet have an object id and that it
        does sync to collaborator after the parent service request object is synced to collaborator and receives its
        object id
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
        self.assertEqual(
            ServiceRequestAttachment.objects.first().exists_on_collaborator, False
        )

        # Then create service request on collaborator
        async_task(
            create_service_request, self.service_request_one.id, [],
        )

        # Now it should be synced since it should have been triggered for syncing after the service request was created
        self.assertEqual(
            ServiceRequestAttachment.objects.first().exists_on_collaborator, True
        )
