from enum import Enum


class JobStatus(Enum):
    INCOMPLETE = "INCOMPLETE"
    COMPLETE = "COMPLETE"
    CANCELED = "CANCELED"
