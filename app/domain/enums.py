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


class SuggestionGenerationType(StrEnum):
    original = "original"
    smaller = "smaller"
    safety_net = "safety_net"


class SuggestionSource(StrEnum):
    rule_based = "rule_based"
    ai = "ai"


class CalendarCandidateType(StrEnum):
    fixed_time = "fixed_time"
    flexible = "flexible"
    deadline_based = "deadline_based"
    routine = "routine"
    recovery = "recovery"


class CalendarPreferredTimeBlock(StrEnum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"
    night = "night"
    anytime = "anytime"


class CalendarEnergyLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class CalendarFrictionLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class CalendarSplitStrategy(StrEnum):
    single_block = "single_block"
    multiple_blocks = "multiple_blocks"
    tiny_first_step = "tiny_first_step"


class CalendarCandidateStatus(StrEnum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    scheduled = "scheduled"
