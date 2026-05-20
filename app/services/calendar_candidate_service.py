import re
from datetime import datetime

from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationDomainError
from app.domain.enums import (
    CalendarCandidateStatus,
    CalendarCandidateType,
    CalendarEnergyLevel,
    CalendarFrictionLevel,
    CalendarPreferredTimeBlock,
    CalendarSplitStrategy,
)
from app.domain.time import utc_now
from app.models import CalendarCandidate, CalendarEvent, Suggestion
from app.repositories.calendar_candidate_repository import CalendarCandidateRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.calendar_service import CalendarService
from app.services.common import require_session, require_suggestion

BIG_TASK_PATTERNS = (
    "제출",
    "완성",
    "마무리",
    "정리",
    "준비",
    "작성",
    "청소",
    "해결",
)
LOW_ENERGY_PATTERNS = ("침대", "귀찮", "부담", "못", "막막", "피곤")
FIXED_TIME_PATTERNS = (
    "오전",
    "오후",
    "시",
    "분",
    "오늘",
    "내일",
    "모레",
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
)
DEADLINE_PATTERNS = ("까지", "마감", "제출", "예약")


class CalendarCandidateService:
    def __init__(self, db: DbSession):
        self.db = db
        self.candidates = CalendarCandidateRepository(db)
        self.suggestions = SuggestionRepository(db)

    def list_for_session(
        self,
        user_id: int,
        session_id: int,
        limit: int = 100,
    ) -> list[CalendarCandidate]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        return self.candidates.list_for_session(user_id, session_id, limit=limit)

    def create_from_suggestions(
        self,
        user_id: int,
        session_id: int,
        suggestion_ids: list[int] | None = None,
    ) -> list[CalendarCandidate]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        suggestions = self._select_suggestions(user_id, session_id, suggestion_ids)
        if not suggestions:
            raise ValidationDomainError(
                "캘린더 후보로 만들 suggestion이 없습니다.",
                code="CALENDAR_CANDIDATE_NO_SUGGESTIONS",
            )

        result: list[CalendarCandidate] = []
        for suggestion in suggestions:
            existing = self.candidates.get_by_suggestion(user_id, suggestion.id)
            if existing is not None:
                result.append(existing)
                continue
            result.append(self._create_candidate_for_suggestion(user_id, suggestion))
        self.db.commit()
        for candidate in result:
            self.db.refresh(candidate)
        return result

    def schedule(
        self,
        user_id: int,
        candidate_id: int,
        start_at: datetime,
        end_at: datetime,
        timezone: str = "Asia/Seoul",
        location: str | None = None,
        placement_source: str = "manual",
        is_locked: bool = False,
        user_note: str | None = None,
    ) -> tuple[CalendarCandidate, CalendarEvent]:
        candidate = self._require_candidate(user_id, candidate_id)
        if candidate.status == CalendarCandidateStatus.scheduled.value:
            raise ValidationDomainError(
                "이미 캘린더에 배치된 후보입니다.",
                code="CALENDAR_CANDIDATE_ALREADY_SCHEDULED",
            )

        event = CalendarService(self.db).create(
            user_id=user_id,
            session_id=candidate.session_id,
            action_id=candidate.action_id,
            candidate_id=candidate.id,
            title=candidate.title,
            description=candidate.micro_step,
            start_at=start_at,
            end_at=end_at,
            timezone=timezone,
            location=location,
            source="calendar_candidate",
            display_color="#C0E1D2",
            is_soft_block=True,
        )
        candidate.status = CalendarCandidateStatus.scheduled.value
        candidate.calendar_event_id = event.id
        candidate.planned_start_at = start_at
        candidate.planned_end_at = end_at
        candidate.placement_source = placement_source
        candidate.is_locked = is_locked
        candidate.user_note = user_note
        candidate.conflict_status = "clear"
        candidate.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(candidate)
        self.db.refresh(event)
        return candidate, event

    def schedule_from_suggestion(
        self,
        user_id: int,
        session_id: int,
        suggestion_id: int,
        start_at: datetime,
        end_at: datetime,
        timezone: str = "Asia/Seoul",
        location: str | None = None,
        placement_source: str = "manual",
        is_locked: bool = False,
        user_note: str | None = None,
    ) -> tuple[CalendarCandidate, CalendarEvent]:
        suggestion = require_suggestion(self.db, user_id, suggestion_id)
        if suggestion.session_id != session_id:
            raise ValidationDomainError(
                "Suggestion이 해당 세션에 속하지 않습니다.",
                code="SUGGESTION_SESSION_MISMATCH",
            )

        existing = self.candidates.get_by_suggestion(user_id, suggestion_id)
        if existing is None or existing.status == CalendarCandidateStatus.scheduled.value:
            candidate = self._create_candidate_for_suggestion(user_id, suggestion)
            self.db.commit()
            self.db.refresh(candidate)
        else:
            candidate = existing

        return self.schedule(
            user_id=user_id,
            candidate_id=candidate.id,
            start_at=start_at,
            end_at=end_at,
            timezone=timezone,
            location=location,
            placement_source=placement_source,
            is_locked=is_locked,
            user_note=user_note,
        )

    def _select_suggestions(
        self,
        user_id: int,
        session_id: int,
        suggestion_ids: list[int] | None,
    ) -> list[Suggestion]:
        if suggestion_ids:
            selected = [
                require_suggestion(self.db, user_id, suggestion_id)
                for suggestion_id in suggestion_ids
            ]
            for suggestion in selected:
                if suggestion.session_id != session_id:
                    raise ValidationDomainError(
                        "Suggestion이 해당 세션에 속하지 않습니다.",
                        code="SUGGESTION_SESSION_MISMATCH",
                    )
            return selected

        return [
            suggestion
            for suggestion in self.suggestions.list_by_session(user_id, session_id)
            if suggestion.generation_type != "smaller"
        ][:5]

    def _create_candidate_for_suggestion(
        self,
        user_id: int,
        suggestion: Suggestion,
    ) -> CalendarCandidate:
        text = f"{suggestion.title} {suggestion.micro_step}"
        estimated_minutes = infer_estimated_minutes(text)
        return self.candidates.create(
            user_id=user_id,
            session_id=suggestion.session_id,
            suggestion_id=suggestion.id,
            title=suggestion.title,
            micro_step=suggestion.micro_step,
            candidate_type=infer_candidate_type(text),
            estimated_minutes=estimated_minutes,
            min_minutes=max(3, estimated_minutes // 2),
            max_minutes=min(60, max(estimated_minutes + 10, estimated_minutes * 2)),
            preferred_time_block=infer_time_block(text),
            energy_level=infer_energy_level(text),
            friction_level=infer_friction_level(text),
            split_strategy=infer_split_strategy(text),
            reason=build_reason(text),
        )

    def _require_candidate(self, user_id: int, candidate_id: int) -> CalendarCandidate:
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            raise NotFoundError(
                "캘린더 후보를 찾을 수 없습니다.",
                code="CALENDAR_CANDIDATE_NOT_FOUND",
            )
        if candidate.user_id != user_id:
            raise PermissionDeniedError(
                "캘린더 후보 접근 권한이 없습니다.",
                code="CALENDAR_CANDIDATE_FORBIDDEN",
            )
        return candidate


def infer_candidate_type(text: str) -> str:
    if any(pattern in text for pattern in DEADLINE_PATTERNS):
        return CalendarCandidateType.deadline_based.value
    if any(pattern in text for pattern in FIXED_TIME_PATTERNS):
        return CalendarCandidateType.fixed_time.value
    if any(pattern in text for pattern in LOW_ENERGY_PATTERNS):
        return CalendarCandidateType.recovery.value
    return CalendarCandidateType.flexible.value


def infer_estimated_minutes(text: str) -> int:
    if re.search(r"\d+\s*(개|장|페이지|쪽|건)", text):
        return 25
    if any(pattern in text for pattern in ("열기", "꺼내기", "한 줄", "첫 줄", "제목만")):
        return 10
    if any(pattern in text for pattern in BIG_TASK_PATTERNS):
        return 25
    return 15


def infer_time_block(text: str) -> str:
    if "오전" in text or "아침" in text:
        return CalendarPreferredTimeBlock.morning.value
    if "오후" in text or "점심" in text:
        return CalendarPreferredTimeBlock.afternoon.value
    if "저녁" in text:
        return CalendarPreferredTimeBlock.evening.value
    if "밤" in text:
        return CalendarPreferredTimeBlock.night.value
    return CalendarPreferredTimeBlock.anytime.value


def infer_energy_level(text: str) -> str:
    if any(pattern in text for pattern in LOW_ENERGY_PATTERNS):
        return CalendarEnergyLevel.low.value
    if any(pattern in text for pattern in ("제출", "발표", "전화", "면접")):
        return CalendarEnergyLevel.high.value
    return CalendarEnergyLevel.medium.value


def infer_friction_level(text: str) -> str:
    if any(pattern in text for pattern in ("전화", "제출", "면접", "병원", "이력서")):
        return CalendarFrictionLevel.high.value
    if any(pattern in text for pattern in ("열기", "꺼내기", "한 줄", "한 모금")):
        return CalendarFrictionLevel.low.value
    return CalendarFrictionLevel.medium.value


def infer_split_strategy(text: str) -> str:
    if any(pattern in text for pattern in BIG_TASK_PATTERNS):
        return CalendarSplitStrategy.tiny_first_step.value
    return CalendarSplitStrategy.single_block.value


def build_reason(text: str) -> str:
    if infer_split_strategy(text) == CalendarSplitStrategy.tiny_first_step.value:
        return "큰 작업으로 느껴질 수 있어 첫 시작 행동 기준으로 캘린더 후보를 만들었습니다."
    return "한 번에 시작 가능한 작은 행동으로 캘린더 후보를 만들었습니다."
