
class Response:
    def __init__(self, status_code=200, headers=None, data=None, text=None):
        self.status_code = status_code
        self.reason = status_code
        self.text = status_code
        self.headers = headers \
            if headers is not None else {"content-type": "application/json"}
        self.data = data
        self.text = text

    def json(self):
        return self.data
