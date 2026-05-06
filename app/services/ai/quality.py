from __future__ import annotations

import re
from collections.abc import Iterable

PRESSURE_WORDS = (
    "실패",
    "실패했다",
    "게으르",
    "무조건",
    "반드시",
    "당장 끝내",
    "성취율",
    "생산성 점수",
    "못하면",
    "왜 안",
    "늦었다",
)

TOO_BIG_PHRASES = (
    "완성하기",
    "끝내기",
    "전부 정리",
    "다 하기",
    "한 번에 처리",
    "전체 작성",
    "프로젝트 마무리",
    "모두 해결",
    "완전히 처리",
)

MULTI_ACTION_MARKERS = (
    "그리고",
    "하고 ",
    "한 뒤",
    "정리하고",
    "작성하고",
    "보내고",
    "확인하고",
)

SMALL_START_MARKERS = (
    "파일 열기",
    "첫 줄",
    "제목만",
    "3개만",
    "한 문장만",
    "버튼 하나",
    "물건 하나",
    "열기",
    "하나만",
)

MAX_TITLE_LENGTH = 40
WARN_MICRO_STEP_LENGTH = 90
MAX_MICRO_STEP_LENGTH = 130


def validate_candidate_quality(title: str, micro_step: str) -> list[str]:
    issues: list[str] = []
    title = title.strip()
    micro_step = micro_step.strip()

    if not title:
        issues.append("error:title_blank")
    if not micro_step:
        issues.append("error:micro_step_blank")
    if title and len(title) > MAX_TITLE_LENGTH:
        issues.append("error:title_too_long")
    if micro_step and len(micro_step) > MAX_MICRO_STEP_LENGTH:
        issues.append("error:micro_step_too_long")
    elif micro_step and len(micro_step) > WARN_MICRO_STEP_LENGTH:
        issues.append("warning:micro_step_long")

    combined = f"{title} {micro_step}"
    if _contains_any(combined, PRESSURE_WORDS):
        issues.append("error:pressure_language")
    if _contains_any(combined, TOO_BIG_PHRASES):
        issues.append("error:action_too_big")
    if _count_markers(micro_step, MULTI_ACTION_MARKERS) >= 2:
        issues.append("warning:multiple_actions_mixed")
    if micro_step and not _has_concrete_start(micro_step):
        issues.append("warning:could_be_more_concrete")

    return issues


def validate_response_quality(response, feature_name: str) -> list[str]:
    issues: list[str] = []
    suggestions = getattr(response, "suggestions", [])
    minimum = 1 if feature_name == "make_smaller" else 2
    maximum = 3 if feature_name == "make_smaller" else 5

    if not minimum <= len(suggestions) <= maximum:
        issues.append("error:invalid_suggestion_count")

    for index, suggestion in enumerate(suggestions):
        title = getattr(suggestion, "title", "")
        micro_step = getattr(suggestion, "micro_step", "")
        issues.extend(
            f"{issue}:suggestion_{index}" for issue in validate_candidate_quality(title, micro_step)
        )

    return issues


def validate_make_smaller_quality(
    original_title: str,
    original_micro_step: str,
    response,
) -> list[str]:
    issues = validate_response_quality(response, feature_name="make_smaller")
    original_text = _normalize(f"{original_title} {original_micro_step}")

    for index, suggestion in enumerate(getattr(response, "suggestions", [])):
        title = getattr(suggestion, "title", "")
        micro_step = getattr(suggestion, "micro_step", "")
        candidate_text = _normalize(f"{title} {micro_step}")
        if candidate_text == original_text:
            issues.append(f"error:make_smaller_same_as_original:suggestion_{index}")
        if _similar_enough(candidate_text, original_text):
            issues.append(f"error:make_smaller_too_similar:suggestion_{index}")
        if len(micro_step.strip()) >= len(
            original_micro_step.strip()
        ) and not _has_small_start_marker(micro_step):
            issues.append(f"error:make_smaller_not_smaller:suggestion_{index}")

    return issues


def hard_failures(issues: Iterable[str]) -> list[str]:
    return [issue for issue in issues if issue.startswith("error:")]


def _contains_any(value: str, words: Iterable[str]) -> bool:
    normalized = _normalize(value)
    return any(_normalize(word) in normalized for word in words)


def _count_markers(value: str, markers: Iterable[str]) -> int:
    return sum(1 for marker in markers if marker in value)


def _has_concrete_start(value: str) -> bool:
    if _has_small_start_marker(value):
        return True
    return bool(
        re.search(r"(쓰기|열기|누르기|고르기|메모하기|적기|치우기|확인하기)$", value.strip())
    )


def _has_small_start_marker(value: str) -> bool:
    return _contains_any(value, SMALL_START_MARKERS)


def _similar_enough(value: str, original: str) -> bool:
    if not value or not original:
        return False
    if value in original or original in value:
        return True
    value_tokens = set(_tokenize(value))
    original_tokens = set(_tokenize(original))
    if not value_tokens or not original_tokens:
        return False
    overlap = len(value_tokens & original_tokens) / len(value_tokens | original_tokens)
    return overlap >= 0.8


def _tokenize(value: str) -> list[str]:
    return [token for token in re.split(r"\W+", value) if token]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())
