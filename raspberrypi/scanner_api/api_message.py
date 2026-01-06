from message import Message
from scanner_message import ScannerMessage


class ApiMessage(Message):

    def __init__(self, status: bool, message: str | bool):
        super().__init__(status, message)
        
    @classmethod
    def success_message_str(cls, message: str):
        return cls(True, message)
    
    @classmethod
    def success_message_bool(cls, message: bool):
        return cls(True, message)
    
    @classmethod
    def from_scanner_message(cls, scanner_message: ScannerMessage):
        return cls(scanner_message.status, scanner_message.message)
