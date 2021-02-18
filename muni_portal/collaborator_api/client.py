import requests
from typing import TypedDict, List

# TODO: remove this before merging PR
EXISTING_TASK_OBJECT_IDS = [
    556704,
    556705,
    556706
]

COLLAB_FIELD_MAP = {
    "type": "F1",
    "user_name": "F2",
    "user_surname": "F3",
    "user_mobile_number": "F4",
    "user_email_address": "F5",
    "municipal_account_number": "F6",
    "street_name": "F7",
    "street_number": "F8",
    "suburb": "F9",
    "description": "F10",
    "coordinates": "F11",
    "request_date": "F12",
    "mobile_reference": "F13",
    "on_premis_reference": "F14",
    "status": "F15",
    "demarcation_code": "F20",
}

# TODO: Move these into settings.py
COLLAB_API_BASE_URL = "https://consumercollab.collaboratoronline.com"
APP_VERSION = "0.1.0"
DEVICE_ID = "OpenUp"


class FormField(TypedDict):
    """ A FormField as defined by Collaborator Web API """
    FieldID: str
    FieldValue: str


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
        if not self.token:
            raise Exception("Auth Token not set. Did you login with authenticate()?")

    def authenticate(self) -> requests.Response:
        """
        Authenticate with the provided username and password from class instantiation.
        """
        url = f"{COLLAB_API_BASE_URL}/webAPI/api/MobileToken/GetTokenForUser"
        request_data = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(url, headers=self.request_headers, json=request_data)
        response.raise_for_status()  # Watch out, they do return 200 for "Auth Failed"

        # Response text has quotes inside the string..
        if str(response.text).lower() == "\"auth failed\"":
            raise Exception("Authentication failed with the provided username and password.")

        self.token = response.json()
        self.request_headers.update({"authorization": f"Bearer {self.token}"})
        return response

    def create_task(self, template_id: int = 9, bp_id: int = 3, percent_complete: int = 10,
                    comments: str = "OpenUp Test", form_fields: List[FormField] = None) -> requests.Response:
        """
        Create a task object

        template_id: Object template reference. We're working with a Service Request workflow, which has ID = 9
        bp_id: Workflow reference. (?)
        percent_complete: Not sure. (Guessing it's the 'progress' of the issue? Not sure how to use it yet.)
        """
        self.__assert_auth__()

        if not form_fields:
            form_fields = []

        url = f"{COLLAB_API_BASE_URL}/webAPIConsumer/api/Task/SaveNewTaskFeedback"
        request_data = {
            "TemplateId": template_id,
            "BPID": bp_id,
            "PercentComplete": percent_complete,
            "Comments": comments,
            "FormFields": form_fields,
        }

        request = requests.Request("POST", url, headers=self.request_headers, json=request_data)
        prepared_request = request.prepare()
        pretty_print_prepared_request(prepared_request)
        response = self.session.send(prepared_request)
        response.raise_for_status()
        return response

    def get_task(self, obj_id: int, template_id: int = 9, fields: List[FormField] = None) -> requests.Response:
        """ Retrieve detail about a task object. """
        self.__assert_auth__()

        url = f"{COLLAB_API_BASE_URL}/webapi/api/Objects/GetObject"
        if fields is None:
            fields = []

        request_data = {
            "template_id": template_id,
            "obj_id": obj_id,
            "Fields": fields,
        }

        request = requests.Request("POST", url, headers=self.request_headers, json=request_data)
        prepared_request = request.prepare()
        pretty_print_prepared_request(prepared_request)
        response = self.session.send(prepared_request)
        response.raise_for_status()
        return response


def pretty_print_prepared_request(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.

    https://stackoverflow.com/a/23816211
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))
