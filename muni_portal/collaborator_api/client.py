import requests
from typing import List
from django.conf import settings
from django.db.models.fields.files import FieldFile
from rest_framework.response import Response

from . import types

APP_VERSION = "0.1.0"
DEVICE_ID = "OpenUp"


class Client:
    """ Main Collaborator Web API class.

    Usage:
        >> client = Client("myusername", "mypassword")
        >> client.authenticate()
        >> client.get_task(1)

    """

    def __init__(self, username: str, password: str) -> None:
        self.request_headers = {
            "accept": "application/json",
            "deviceId": DEVICE_ID,
            "appVersion": APP_VERSION,
        }
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.token = None

    def __assert_auth__(self) -> None:
        """ Assert that the client has logged in and has a token set. """
        if not self.token:
            raise Exception("Auth Token not set. Did you login with authenticate()?")

    def authenticate(self) -> requests.Response:
        """
        Authenticate with the provided username and password from class instantiation.
        """
        url = f"{settings.COLLABORATOR_API_BASE_URL}/webAPI/api/MobileToken/GetTokenForUser"
        request_data = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(url, headers=self.request_headers, json=request_data)
        response.raise_for_status()

        # Response text has quotes inside the string..
        if str(response.text).lower() == '"auth failed"':
            raise Exception(
                "Authentication failed with the provided username and password."
            )

        self.token = response.json()
        self.request_headers.update({"authorization": f"Bearer {self.token}"})
        return response

    def create_task(
        self,
        form_fields: List[types.FormField],
        template_id: int = 9,
        bp_id: int = 3,
        percent_complete: int = 10,
        comments: str = "",
    ) -> requests.Response:
        """
        Create a task object

        template_id: Object template reference. We're working with a Service Request workflow, which has ID = 9
        bp_id: Workflow reference. (?)
        percent_complete: Not sure. (Guessing it's the 'progress' of the issue? Not sure how to use it yet.)
        """
        self.__assert_auth__()

        if not form_fields:
            form_fields = []

        if settings.ENVIRONMENT != "production":
            comments += (
                f"  (Created by Cape Agulhas App {settings.ENVIRONMENT} environment)"
            )

        url = (
            f"{settings.COLLABORATOR_API_BASE_URL}/webAPI/api/Task/SaveNewTaskFeedback"
        )
        request_data = {
            "TemplateId": template_id,
            "BPID": bp_id,
            "PercentComplete": percent_complete,
            "Comments": comments,
            "FormFields": form_fields,
        }

        response = self.session.post(
            url, headers=self.request_headers, json=request_data
        )
        response.raise_for_status()
        return response

    def get_task(
        self, obj_id: int, template_id: int = 9, fields: List[types.FormField] = None
    ) -> types.ServiceRequestObject:
        """ Retrieve detail about a task object. """
        self.__assert_auth__()

        url = f"{settings.COLLABORATOR_API_BASE_URL}/webapi/api/Objects/GetObject"
        if fields is None:
            fields = []

        request_data = {
            "template_id": template_id,
            "obj_id": obj_id,
            "Fields": fields,
        }

        response = self.session.post(
            url, headers=self.request_headers, json=request_data
        )
        response.raise_for_status()

        obj_list = response.json().get("Data").get("ObjectList")
        if len(obj_list) > 1:
            raise AssertionError("Returned object list has more than one object")
        elif len(obj_list) < 1:
            raise AssertionError("Returned object list has less than one object")

        obj = obj_list[0][0]
        return obj

    def create_attachment(
        self, obj_id: int, attachment: FieldFile, content_type: str
    ) -> Response:
        """ Create an attachment for an existing Service Request """
        self.__assert_auth__()

        url = f"{settings.COLLABORATOR_API_BASE_URL}/webapi/api/File/Post"

        name = attachment.name.split("/")[-1]

        files = [
            ("Attachment", (name, attachment.open(mode="rb").read(), content_type),),
        ]

        attachment.close()

        response = self.session.post(
            url, headers=self.request_headers, files=files, data={"Obj_Id": f"{obj_id}"}
        )
        response.raise_for_status()

        return response

    def create_update_record(
        self, obj_id: int, status: str, status_tag="F15"
    ) -> Response:
        """
        Create an 'update record' which effectively updates a Service Request object in this app's context

        We use this endpoint to change the status of a Service Request which in turn triggers the upload process
        from Collaborator to On Prem. We need to trigger this process after creating attachments for a Service Request
        so that the attachments are included in the upload process.
        """

        self.__assert_auth__()

        url = f"{settings.COLLABORATOR_API_BASE_URL}/webapi/Api/Records/CreateUpdateRecord"

        headers = self.request_headers
        headers["Content-Type"] = "application/xml"

        data = f"""
            <Objects>
                <ServiceRequest>
                    <ObjectId>{obj_id}</ObjectId>
                    <{status_tag}>{status}</{status_tag}>
                </ServiceRequest>
            </Objects>
        """

        response = self.session.post(url, headers=headers, data=data)
        response.raise_for_status()
        if not response.json() == str(obj_id):
            raise AssertionError(f"Create Update Record API call failed for Object ID {obj_id}")

        return response
