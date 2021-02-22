from typing import TypedDict


class FormField(TypedDict):
    """ A FormField as defined by Collaborator Web API """
    FieldID: str
    FieldValue: str


class ServiceRequestObject(TypedDict):
    """ Service Request object as returned by Collaborator Web API """
    obj_id: int
    template_id: int
    F0: str
    F1: str
    F2: str
    F3: str
    F4: str
    F5: str
    F6: str
    F7: str
    F8: str
    F9: str
    F10: str
    F11: str
    F12: str
    F13: str
    F14: str
    F15: str
    F18: str
    F19: str
    F25: str
