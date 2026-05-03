from enum import StrEnum


class ActionStatus(StrEnum):
    active = "active"
    completed = "completed"
    aborted = "aborted"


class FeedbackType(StrEnum):
    do = "do"
    snooze = "snooze"
    pass_ = "pass"
    make_smaller = "make_smaller"
    capture_only = "capture_only"
