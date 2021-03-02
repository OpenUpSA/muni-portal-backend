from unittest import mock

from django.contrib.auth.models import User
from requests import Session

from muni_portal.core.models import ServiceRequest
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

MOCK_GET_TASK_DETAIL_RESPONSE_JSON = {
    "Code": 0,
    "Message": "Success",
    "DetailedMessages": None,
    "CollaboratorUri": "https://consumercollab.collaboratoronline.com/collab/",
    "Data": {
        "tmpCollabObject": {
            "obj_id": 1,
            "template_id": 9,
            "Fields": []
        },
        "ObjectList": [
            [
                {
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
                    "F25": "WC033"
                }
            ]
        ]
    }
}

MOCK_GET_TASK_LIST_RESPONSE_JSON = {
    "Code": 0,
    "Message": "Success",
    "DetailedMessages": None,
    "CollaboratorUri": "https://consumercollab.collaboratoronline.com/collab/",
    "Data": {
        "tmpCollabObject": {
            "obj_id": 1,
            "template_id": 9,
            "Fields": []
        },
        "ObjectList": [
            [
                {
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
                    "F25": "WC033"
                },
                {
                    "obj_id": 2,
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
                    "F25": "WC033"
                }
            ]
        ]
    }
}


class ApiServiceRequestTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.password = Faker().password(length=8)
        cls.user = User.objects.create_user(
            username="test", email="test@test.com", password=cls.password
        )
        cls.service_request_one = ServiceRequest.objects.create(collaborator_object_id=1, user=cls.user)
        cls.service_request_two = ServiceRequest.objects.create(collaborator_object_id=2, user=cls.user)

    def authenticate(self):
        data = {"username": self.user.username, "password": self.password}
        response = self.client.post(reverse("token_obtain_pair"), data=data)
        jwt_token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, 'post')
    def test_get_detail(self, mock_session_post, mock_post):
        mock_auth_response = mock.Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = "testToken"
        mock_post.return_value = mock_auth_response

        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_GET_TASK_DETAIL_RESPONSE_JSON
        mock_session_post.return_value = mock_detail_response

        self.authenticate()

        response = self.client.get(reverse("service-request-detail", kwargs={"pk": self.service_request_one.pk}))
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
            "status": "in_progress",
            "demarcation_code": "WC033",
            "user": 4
        }
        self.assertDictEqual(response.data, expected_response_data)

    @mock.patch("muni_portal.collaborator_api.client.requests.post")
    @mock.patch.object(Session, 'post')
    def test_get_list(self, mock_session_post, mock_post):
        mock_auth_response = mock.Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = "testToken"
        mock_post.return_value = mock_auth_response

        mock_detail_response = mock.Mock()
        mock_detail_response.status_code = 200
        mock_detail_response.json.return_value = MOCK_GET_TASK_DETAIL_RESPONSE_JSON
        mock_session_post.return_value = mock_detail_response

        self.authenticate()

        response = self.client.get(reverse("service-request-list-create"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected_response_data = ({
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
            "status": "in_progress",
            "demarcation_code": "WC033",
            "user": 4
        }, {
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
            "status": "in_progress",
            "demarcation_code": "WC033",
            "user": 4
        })
        sorted_response = sorted(response.data, key=lambda k: k['id'])
        self.assertDictEqual(sorted_response[0], expected_response_data[0])
        self.assertDictEqual(sorted_response[1], expected_response_data[1])
