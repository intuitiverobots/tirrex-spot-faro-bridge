import requests
from requests import RequestException

from scanner_message import ScannerMessage

from CONST import URL_SCANNER_API, REQUEST_TIMEOUT


class Requester:

    @staticmethod
    def get(url: str) -> ScannerMessage:
        try:
            return ScannerMessage.from_response(requests.get(f"{URL_SCANNER_API}/{url}", timeout=REQUEST_TIMEOUT))
        except RequestException as ex:
            return ScannerMessage.error_message(f"error get request '{url}': {ex}")
        
    @staticmethod
    def post(url: str, params: str="") -> ScannerMessage:
        try:
            return ScannerMessage.from_response(requests.post(f"{URL_SCANNER_API}/{url}", data=params, timeout=REQUEST_TIMEOUT))
        except RequestException as ex:
            return ScannerMessage.error_message(f"error post request '{url}' with params '{params}': {ex}")
