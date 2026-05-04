AI_SUGGESTION_SYSTEM_PROMPT = """
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
"""


def build_brain_dump_input(
    raw_text: str,
    session_context: str | None = None,
    effort_context: str | None = None,
) -> str:
    parts = [
        "task: brain_dump_suggestions",
        "prompt_version: v1",
        "Brain Dump 입력:",
        raw_text,
    ]
    if session_context:
        parts.extend(["세션 context_note:", session_context])
    if effort_context:
        parts.extend(["현재 mode/effort context:", effort_context])
    parts.append("생성 개수: 2~5")
    return "\n".join(parts)


def build_make_smaller_input(title: str, micro_step: str) -> str:
    return "\n".join(
        [
            "task: make_smaller",
            "prompt_version: v1",
            "아래 suggestion이 부담스럽게 느껴질 수 있다.",
            "기존보다 반드시 더 작은 시작 행동 1~3개로 나눠라.",
            "파일 열기, 제목만 쓰기, 첫 줄만 쓰기, 3개만 정리하기 같은 시작 행동 중심으로 만든다.",
            f"title: {title}",
            f"micro_step: {micro_step}",
        ]
    )
