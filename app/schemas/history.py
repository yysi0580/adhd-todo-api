from pydantic import BaseModel

from app.schemas.action import ActionRead
from app.schemas.brain_dump import BrainDumpRead
from app.schemas.feedback import FeedbackRead
from app.schemas.session import SessionRead


class HistoryResponse(BaseModel):
    sessions: list[SessionRead]
    brain_dumps: list[BrainDumpRead]
    actions: list[ActionRead]
    feedback: list[FeedbackRead]
