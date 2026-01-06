from time import sleep
import threading

from requester import Requester
from api_message import ApiMessage
from job import Job
from job_status import JobStatus

from CONST import URL_SCANNER_API, UPDATE_CURRENT_JOB_LOOP_TIME, SCAN_FILE_SETTINGS


def checkers(*checkers):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            for check in checkers:
                result = check(self)
                if result is not None:
                    return result
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class Scanner:

    def __init__(self):
        self._is_connected: bool = False
        self._battery: float = 0.0
        self._storage: float = 0.0
        self._current_job: Job = None
        self._old_jobs: list[Job] = []
    
    def update_scanner(self) -> None:
        scanner_message = Requester.get("scanner-state")
        if scanner_message.is_error():
            self._is_connected = False
            print("error: couldn't connect to scanner")
            return
        else:
            if not self._is_connected:
                print("connected to scanner")
                self._is_connected = True
        json = scanner_message.json
        if json["battery"] is not None:
            self._battery = json["battery"]["chargeLevel"]
        if json["sdCard"] is not None:
            capacity = json["sdCard"]["capacity"]
            free_space = json["sdCard"]["freeSpace"]
            self._storage = (capacity - free_space) / capacity

    def _ensure_is_connected(self) -> ApiMessage | None:
        if not self._is_connected:
            return ApiMessage.error_message("not connected to scanner")
    
    def _ensure_is_not_scanning(self) -> ApiMessage | None:
        if self._current_job is not None:
            return ApiMessage.error_message("scanner is already scanning")
    
    def _ensure_is_scanning(self) -> ApiMessage | None:
        if self._current_job is None:
            return ApiMessage.error_message("scanner is not scanning")

    @checkers(_ensure_is_connected, _ensure_is_not_scanning)
    def start_scan(self) -> ApiMessage:        
        with open(SCAN_FILE_SETTINGS, "r") as f:
            settings = f.read()
        scanner_message = Requester.post("jobs", settings)
        if scanner_message.is_error():
            return ApiMessage.from_scanner_message(scanner_message)
        self._current_job = Job(scanner_message)
        threading.Thread(target=self._update_current_job, daemon=True).start()
        return ApiMessage.success_message_str("scan has started")

    def _update_current_job(self) -> None:
        while self._current_job.status == JobStatus.INCOMPLETE:
            self._current_job.update()
            sleep(UPDATE_CURRENT_JOB_LOOP_TIME)
        self._old_jobs.append(self._current_job)
        self._current_job = None

    @checkers(_ensure_is_connected)
    def is_scanning(self) -> ApiMessage:
        return ApiMessage.success_message_bool(self._current_job is not None)

    @checkers(_ensure_is_connected, _ensure_is_scanning)
    def abort_scan(self) -> ApiMessage:
        if self._current_job.abort():
            return ApiMessage.success_message_str("the current job has been aborted")
        else:
            return ApiMessage.error_message("the current job couldn't be aborted")

    def get_stream_info(self) -> tuple[str, str]:
        while not self._current_job.is_stream_ready():
            sleep(UPDATE_CURRENT_JOB_LOOP_TIME)
        stream_url, scan_name = self._current_job.get_stream_info()
        return f"{URL_SCANNER_API}/{stream_url}", scan_name
