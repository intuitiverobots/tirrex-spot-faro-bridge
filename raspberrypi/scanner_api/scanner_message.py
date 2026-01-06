import requests
from json import loads as json_loads

from message import Message


class ScannerMessage(Message):

    def __init__(self, status: bool, message: str):
        super().__init__(status, message)
        self.json: dict = {}
        if self.status and self.message != "":
            self.json = json_loads(message)

    @classmethod
    def from_response(cls, response: requests.Response):
        return cls(response.ok, response.text)
