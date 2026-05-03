def build_smaller_steps(text: str, limit: int = 3) -> list[dict[str, str]]:
    steps = _candidate_steps(text)
    base = text.strip()
    return [
        {
            "title": step,
            "micro_step": step,
            "effort_level": "nano",
        }
        for step in steps
        if step != base
    ][:limit]


def build_smaller_step(text: str) -> dict[str, str]:
    return build_smaller_steps(text, limit=1)[0]


def _candidate_steps(text: str) -> list[str]:
    base = text.strip()
    if any(keyword in base for keyword in ["발표", "슬라이드", "자료"]):
        return [
            "발표 자료 파일만 열기",
            "첫 번째 슬라이드 제목만 적기",
            "참고 자료 링크 1개만 붙여넣기",
        ]
    if any(keyword in base for keyword in ["메일", "email", "이메일"]):
        return [
            "메일 작성 창만 열기",
            "받는 사람만 입력하기",
            "첫 문장만 쓰기",
        ]
    if any(keyword in base for keyword in ["정리", "책상", "자료"]):
        return [
            "관련 파일 1개만 열기",
            "눈에 보이는 항목 3개만 정리하기",
            "제목만 쓰기",
        ]
    return [
        f"'{base[:24]}' 관련 화면만 열기",
        "제목만 쓰기",
        "첫 줄만 쓰기",
    ]
