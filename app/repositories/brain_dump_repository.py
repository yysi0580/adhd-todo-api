from sqlalchemy.orm import Session as DbSession

from app.models import BrainDump


class BrainDumpRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def list_by_session(self, user_id: int, session_id: int) -> list[BrainDump]:
        return (
            self.db.query(BrainDump)
            .filter(BrainDump.user_id == user_id, BrainDump.session_id == session_id)
            .order_by(BrainDump.created_at.desc())
            .all()
        )

    def list_recent_for_user(self, user_id: int, limit: int = 20) -> list[BrainDump]:
        return (
            self.db.query(BrainDump)
            .filter(BrainDump.user_id == user_id)
            .order_by(BrainDump.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, user_id: int, session_id: int, raw_text: str) -> BrainDump:
        brain_dump = BrainDump(user_id=user_id, session_id=session_id, raw_text=raw_text)
        self.db.add(brain_dump)
        self.db.flush()
        return brain_dump
