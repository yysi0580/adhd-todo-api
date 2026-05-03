from sqlalchemy.orm import Session as DbSession

from app.models import BrainDump


class BrainDumpRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def create(self, session_id: int, raw_text: str) -> BrainDump:
        brain_dump = BrainDump(session_id=session_id, raw_text=raw_text)
        self.db.add(brain_dump)
        self.db.flush()
        return brain_dump
