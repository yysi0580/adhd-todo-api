from app.core.config import get_settings

PROMPT_VERSION_V1 = "v1"
PROMPT_VERSION_V2 = "v2"

AI_SUGGESTION_SYSTEM_PROMPTS = {
    PROMPT_VERSION_V1: """
prompt_version: v1
너는 ADHD 사용자의 실행 부담을 줄이는 행동 분해 도우미다.
사용자를 평가하지 않는다.
우선순위를 강요하지 않는다.
실패, 성취율, 생산성 점수 같은 표현을 쓰지 않는다.
입력된 생각을 2~5분 안에 시작 가능한 작은 행동 후보로 바꾼다.
처음부터 하나만 고르지 말고 여러 개 후보를 만든다.
사용자가 선택할 수 있게 한다.
각 후보는 2~5분 안에 시작 가능한 실제 행동이어야 한다.
반드시 JSON schema에 맞는 structured output만 생성한다.
""",
    PROMPT_VERSION_V2: """
prompt_version: v2
너는 ADHD 사용자의 실행 부담을 줄이는 행동 분해 도우미다.
사용자를 평가하지 않는다.
우선순위를 강요하지 않는다.
실패, 게으름, 성취율, 생산성 점수 같은 표현을 쓰지 않는다.
입력된 생각을 "완료할 일"이 아니라 "시작할 수 있는 후보"로 바꾼다.
각 후보는 2~5분 안에 시작 가능해야 한다.
한 후보에는 하나의 행동만 담는다.
여러 일을 한 후보에 묶지 않는다.
처음부터 하나만 고르지 말고 사용자가 고를 수 있게 2~5개 후보를 만든다.
title은 짧고, micro_step은 실제 행동 문장으로 쓴다.
"완성하기", "끝내기", "전부 처리" 대신 "열기", "첫 줄 쓰기", "3개만 고르기"처럼 시작 행동을 쓴다.
결과는 반드시 지정된 JSON schema를 따른다.
""",
}

AI_SUGGESTION_SYSTEM_PROMPT = AI_SUGGESTION_SYSTEM_PROMPTS[PROMPT_VERSION_V2]


def current_prompt_version() -> str:
    version = get_settings().ai_prompt_version
    if version not in AI_SUGGESTION_SYSTEM_PROMPTS:
        return PROMPT_VERSION_V2
    return version


def current_system_prompt() -> str:
    return AI_SUGGESTION_SYSTEM_PROMPTS[current_prompt_version()]


def build_brain_dump_input(
    raw_text: str,
    session_context: str | None = None,
    effort_context: str | None = None,
) -> str:
    version = current_prompt_version()
    parts = [
        "task: brain_dump_suggestions",
        f"prompt_version: {version}",
    ]
    if version == PROMPT_VERSION_V2:
        parts.extend(
            [
                "품질 규칙:",
                "- 너무 큰 일은 첫 시작 행동으로 줄인다.",
                "- 완성하기/끝내기 대신 열기/첫 줄 쓰기/3개만 고르기 같은 시작 행동을 쓴다.",
                "- 입력 안의 여러 일을 후보로 나누되 우선순위를 단정하지 않는다.",
                "- 입력에 나온 대상과 행동을 반드시 반영한다.",
                "- 입력과 무관한 일반적인 메모장 열기, 마음챙김 제안으로 대체하지 않는다.",
                "- 주변 관찰처럼 입력 밖의 행동 후보를 만들지 않는다.",
                "- 사용자가 부담 없이 고를 수 있게 후보를 만든다.",
                "- 한 후보에는 하나의 행동만 담는다.",
            ]
        )
    parts.extend(["Brain Dump 입력:", raw_text])
    if session_context:
        parts.extend(["세션 context_note:", session_context])
    if effort_context:
        parts.extend(["현재 mode/effort context:", effort_context])
    parts.append("생성 개수: 2~5")
    return "\n".join(parts)


def build_make_smaller_input(title: str, micro_step: str) -> str:
    version = current_prompt_version()
    parts = [
        "task: make_smaller",
        f"prompt_version: {version}",
        "아래 suggestion이 부담스럽게 느껴질 수 있다.",
    ]
    if version == PROMPT_VERSION_V2:
        parts.extend(
            [
                "원본보다 반드시 더 작은 시작 행동 1~3개로 나눠라.",
                "원본을 같은 말로 반복하지 않는다.",
                "행동 하나만 남긴다.",
                "30초~2분 안에 시작 가능한 수준까지 줄인다.",
                "예: 파일 열기, 첫 문장만 쓰기, 버튼 하나만 누르기, 물건 하나만 치우기.",
            ]
        )
    else:
        parts.extend(
            [
                "기존보다 반드시 더 작은 시작 행동 1~3개로 나눠라.",
                "파일 열기, 제목만 쓰기, 첫 줄만 쓰기 같은 시작 행동 중심으로 만든다.",
            ]
        )
    parts.extend([f"title: {title}", f"micro_step: {micro_step}"])
    return "\n".join(parts)
