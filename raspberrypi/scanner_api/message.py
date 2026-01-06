class Message:

    def __init__(self, status: bool, message: str | bool):
        self.status: bool = status
        self.message: str | bool = message

    @classmethod
    def error_message(cls, error: str):
        return cls(False, error)

    def is_error(self) -> bool:
        return not self.status
