from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    COMPLETED = "completed"
