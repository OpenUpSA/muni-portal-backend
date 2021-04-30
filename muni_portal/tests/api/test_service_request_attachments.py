from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.test import APITestCase

from unittest import mock

from django.contrib.auth.models import User
from requests import Session
from rest_framework.exceptions import ErrorDetail
from PIL import Image
from muni_portal.core.models import ServiceRequest, ServiceRequestAttachment
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase


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
    def generate_fake_img() -> ContentFile:
        file = BytesIO()
        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return ContentFile(file.read(), 'test.png')

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_get_list(self, mock_post):
        """ Test GET detail view returns correct schema and values """
        mock_post.return_value = self.get_mock_auth_response()
        self.authenticate()

        attachment = ServiceRequestAttachment.objects.create(
            service_request=self.service_request_one,
            file=self.generate_fake_img(),
            content_type='image/png'
        )

        response = self.client.get(
            reverse(
                "service-request-attachment-list-create",
                kwargs={"service_request_pk": self.service_request_one.pk},
            )
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected_response_data = {
            "id": attachment.id,
            "file": settings.MEDIA_URL + attachment.file.name,
            "date_created": attachment.date_created.isoformat()[:-6] + 'Z',
            "exists_on_collaborator": False,
        }

        self.assertDictEqual(dict(response.data[0]), expected_response_data)
