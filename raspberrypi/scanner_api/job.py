from scanner_message import ScannerMessage
from job_status import JobStatus
from requester import Requester


class Job:

    def __init__(self, scanner_message: ScannerMessage):
        json = scanner_message.json
        self._job_id: str = json["jobId"]
        self._scan_id: str = json["scanId"]
        self.status: JobStatus = JobStatus.INCOMPLETE
        self._progress: int = 0
        self._scan_name: str = None

    def update(self) -> None:
        scanner_message = Requester.get(f"jobs/{self._job_id}")
        if scanner_message.is_error():
            self._error(f"update request error:\n{scanner_message.message}")
        json = scanner_message.json
        if self._scan_name is None and "scanName" in json:
            self._scan_name = json["scanName"]
        if json["status"] == JobStatus.INCOMPLETE:
            self._progress = json["progress"]
        else:
            match json["status"]:
                case JobStatus.COMPLETE.value:
                    self.status = JobStatus.COMPLETE
                case JobStatus.CANCELED.value:
                    self.status = JobStatus.CANCELED
    
    def pause(self) -> bool:
        scanner_message = Requester.post(f"jobs/{self._job_id}/pause")
        if scanner_message.is_error():
            self._error(f"pause request error:\n{scanner_message.message}")
            return False
        return True

    def resume(self) -> bool:
        scanner_message = Requester.post(f"jobs/{self._job_id}/resume")
        if scanner_message.is_error():
            self._error(f"resume request error:\n{scanner_message.message}")
            return False
        return True
    
    def abort(self) -> bool:
        scanner_message = Requester.post(f"jobs/{self._job_id}/abort")
        if scanner_message.is_error():
            self._error(f"abort request error:\n{scanner_message.message}")
            return False
        return True

    def _error(self, message: str) -> None:
        self.status = JobStatus.CANCELED
        print(f"error in job '{self._job_id}': {message}")

    def is_stream_ready(self) -> bool:
        return self._scan_name is not None

    def get_stream_info(self) -> tuple[str, str]:
        return f"jobs/{self._job_id}/{self._scan_name}.zip", self._scan_name
