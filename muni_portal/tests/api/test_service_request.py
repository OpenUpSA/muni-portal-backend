from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from faker import Faker
from requests import Session
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from muni_portal.core.models import ServiceRequest
from muni_portal.tests.api.common_mock_values import (
    MOCK_GET_TASK_DETAIL_RESPONSE_JSON,
    MOCK_CREATE_TASK_RESPONSE_JSON,
)


class ApiServiceRequestTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = Faker().password(length=8)
        cls.user = User.objects.create_user(
            username="test", email="test@test.com", password=cls.password
        )
        cls.service_request_one = ServiceRequest.objects.create(
            collaborator_object_id=1, user=cls.user
        )
        cls.service_request_two = ServiceRequest.objects.create(
            collaborator_object_id=2, user=cls.user
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
    def get_mock_detail_response() -> mock.Mock:
        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_GET_TASK_DETAIL_RESPONSE_JSON
        return mock_detail_response

    @staticmethod
    def get_mock_create_response() -> mock.Mock:
        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_CREATE_TASK_RESPONSE_JSON
        return mock_detail_response

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, "post")
    def test_get_detail(self, mock_session_post, mock_post):
        """ Test GET detail view returns correct schema and values """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_detail_response()
        self.authenticate()

        response = self.client.get(
            reverse(
                "service-request-detail", kwargs={"pk": self.service_request_one.pk}
            )
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected_response_data = {
            "id": 1,
            "collaborator_object_id": 1,
            "type": "Sewerage",
            "user_name": "Mr JD",
            "user_surname": "Bothma",
            "user_mobile_number": "0792816737",
            "user_email_address": "jd@openup.org.za",
            "municipal_account_number": None,
            "street_name": "Geen Straat",
            "street_number": "123",
            "suburb": "Daar",
            "description": "This one has the date 2020-02-01 sent from the app",
            "coordinates": "12.3, 45.6",
            "request_date": "2020-02-01T00:00:00Z",
            "on_premis_reference": "373761",
            "collaborator_status": "assigned",
            "status": "assigned",
            "demarcation_code": "WC033",
            "user": 4,
        }
        self.assertDictEqual(response.data, expected_response_data)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, "post")
    def test_get_list(self, mock_session_post, mock_post):
        """ Test GET list returns correct schema and list """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_detail_response()

        self.authenticate()

        response = self.client.get(reverse("service-request-list-create"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected_response_data = (
            {
                "id": 1,
                "collaborator_object_id": 1,
                "type": "Sewerage",
                "user_name": "Mr JD",
                "user_surname": "Bothma",
                "user_mobile_number": "0792816737",
                "user_email_address": "jd@openup.org.za",
                "municipal_account_number": None,
                "street_name": "Geen Straat",
                "street_number": "123",
                "suburb": "Daar",
                "description": "This one has the date 2020-02-01 sent from the app",
                "coordinates": "12.3, 45.6",
                "request_date": "2020-02-01T00:00:00Z",
                "on_premis_reference": "373761",
                "collaborator_status": "assigned",
                "status": "assigned",
                "demarcation_code": "WC033",
                "user": 4,
            },
            {
                "id": 2,
                "collaborator_object_id": 2,
                "type": "Sewerage",
                "user_name": "Mr JD",
                "user_surname": "Bothma",
                "user_mobile_number": "0792816737",
                "user_email_address": "jd@openup.org.za",
                "municipal_account_number": None,
                "street_name": "Geen Straat",
                "street_number": "123",
                "suburb": "Daar",
                "description": "This one has the date 2020-02-01 sent from the app",
                "coordinates": "12.3, 45.6",
                "request_date": "2020-02-01T00:00:00Z",
                "on_premis_reference": "373761",
                "collaborator_status": "assigned",
                "status": "assigned",
                "demarcation_code": "WC033",
                "user": 4,
            },
        )
        sorted_response = sorted(response.data, key=lambda k: k["id"])
        self.assertDictEqual(sorted_response[0], expected_response_data[0])
        self.assertDictEqual(sorted_response[1], expected_response_data[1])

    @mock.patch.object(Session, "post")
    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    def test_post_create(self, mock_post, mock_session_post):
        """ Test POST create syncs with collaborator and saves collaborator object id """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_create_response()
        self.authenticate()

        ServiceRequest.objects.all().delete()
        self.assertEqual(ServiceRequest.objects.all().count(), 0)

        data = {
            "type": "test-type",
            "user_name": "test name",
            "user_surname": "test surname",
            "user_mobile_number": "test number",
            "street_name": "test street",
            "street_number": "test number",
            "suburb": "JD's burb :)",
            "description": "test description",
        }
        response = self.client.post(reverse("service-request-list-create"), data=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceRequest.objects.all().count(), 1)

        service_request = ServiceRequest.objects.first()

        self.assertEqual(service_request.collaborator_object_id, 1)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, "post")
    def test_post_create_validation(self, mock_session_post, mock_post):
        """ Test that the POST create view returns basic field-level validation errors """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_detail_response()
        self.authenticate()

        data = {
            "type": "test-type",
            "user_name": "test name",
            "user_surname": "test surname",
            "user_mobile_number": "test number",
            "user_email_address": "123",
            "street_name": "test street",
            "street_number": "test number",
            "suburb": "JD's burb :)",
            "description": "super long! " * 1000,  # make a super long description
        }
        response = self.client.post(reverse("service-request-list-create"), data=data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEquals(type(response.data["description"][0]), ErrorDetail)
        self.assertEquals(
            response.data["description"][0],
            "Ensure this field has no more than 1024 characters.",
        )

        self.assertEquals(type(response.data["user_email_address"][0]), ErrorDetail)
        self.assertEquals(
            response.data["user_email_address"][0], "Enter a valid email address."
        )

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, "post")
    def test_post_create_missing_fields(self, mock_session_post, mock_post):
        """ Test that POST create complains if fields are missing """
        mock_post.return_value = self.get_mock_auth_response()
        mock_session_post.return_value = self.get_mock_detail_response()
        self.authenticate()

        response = self.client.post(reverse("service-request-list-create"))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEquals(response.data["type"], "This field is required.")
        self.assertEquals(response.data["user_name"], "This field is required.")
        self.assertEquals(response.data["user_surname"], "This field is required.")
        self.assertEquals(
            response.data["user_mobile_number"], "This field is required."
        )
        self.assertEquals(response.data["description"], "This field is required.")
