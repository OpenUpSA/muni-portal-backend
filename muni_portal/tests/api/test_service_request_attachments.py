from io import BytesIO
from unittest import mock

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from muni_portal.core.models import ServiceRequest, ServiceRequestAttachment


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
            file=cls.generate_fake_img(),
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
    def generate_fake_img() -> ContentFile:
        file = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return ContentFile(file.read(), "test.png")

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
        self.assertEquals(response['Content-Type'], self.attachment_one.content_type)
        self.assertEquals(type(response.content), bytes)
