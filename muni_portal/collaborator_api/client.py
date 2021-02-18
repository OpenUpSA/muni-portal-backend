import requests

# TODO: remove this before merging PR
EXISTING_TASK_OBJECT_IDS = [
    556704,
    556705,
    556706
]

code_table = {
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

COLLAB_API_BASE_URL = "https://consumercollab.collaboratoronline.com"
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
                    comments: str = "OpenUp Test") -> None:
        """
        Create a task object

        template_id: Object template reference. We're working with a Service Request workflow, which has ID = 9
        bp_id: Workflow reference. That's all we know so far.
        percent_complete: Not sure. (Guessing it's the 'progress' of the issue? Not sure how to use it yet.)
        """
        url = f"{COLLAB_API_BASE_URL}/webAPIConsumer/api/Task/SaveNewTaskFeedback"
        request_data = {
            "TemplateId": template_id,
            "BPID": bp_id,
            "PercentComplete": percent_complete,
            "Comments": comments,
            "FormFields": [
                {"FieldID": "F1", "FieldValue": "Roads"},
                {"FieldID": "F2", "FieldValue": "JD"},
                {"FieldID": "F3", "FieldValue": "Bothma"},
                {"FieldID": "F4", "FieldValue": "0792816737"},
                {"FieldID": "F5", "FieldValue": "jd@openup.org.za"},
                {"FieldID": "F6", "FieldValue": "1234567"},
                {"FieldID": "F7", "FieldValue": "Here street"},
                {"FieldID": "F8", "FieldValue": "123"},
                {"FieldID": "F9", "FieldValue": "there suburb"},
                {"FieldID": "F10", "FieldValue": "This is a test. If you see this, please email me."},
                {"FieldID": "F12", "FieldValue": "2020-11-03"},
            ],
        }

        request = requests.Request("POST", url, headers=self.request_headers, json=request_data)
        prepared_request = request.prepare()
        pretty_print_prepared_request(prepared_request)
        result = self.session.send(prepared_request)

        # returns 401 when auth header not provided.
        # Returns 500 for some error with text {"Message":"An error has occurred."}
        print(result.text)
        result.raise_for_status()

        print(result.json())

    def get_task(self, obj_id: int, template_id: int = 9, fields: list = None):
        """ Retrieve detail about a task object. """
        url = f"{COLLAB_API_BASE_URL}/webapi/api/Objects/GetObject"
        if fields is None:
            fields = []
        if not self.token:
            raise Exception("Auth Token not set. Did you login with authenticate()?")

        request_data = {
            "template_id": template_id,
            "obj_id": obj_id,
            "Fields": fields,
        }

        request = requests.Request("POST", url, headers=self.request_headers, json=request_data)
        prepared_request = request.prepare()
        pretty_print_prepared_request(prepared_request)
        result = self.session.send(prepared_request)

        # returns 401 when auth header not provided.
        # Returns 500 for some error with text {"Message":"An error has occurred."}
        print(result.text)
        result.raise_for_status()
        print(result.json())


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
