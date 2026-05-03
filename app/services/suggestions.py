import re


SAFETY_NET_ACTIONS = [
    ("물 한 컵 마시기", "컵에 물을 따르고 한 모금 마시기"),
    ("책상 위 3개만 치우기", "눈앞에 보이는 물건 3개만 제자리로 옮기기"),
    ("제목만 쓰기", "해야 할 일의 제목 한 줄만 작성하기"),
]


def generate_micro_steps(raw_text: str, limit: int = 5) -> list[dict[str, str]]:
    normalized = re.sub(r"\s+", " ", raw_text).strip()
    parts = [
        part.strip(" .,!?\t")
        for part in re.split(r"[,\n]| 그리고 | 하고 | 해야 하고 | 해야함|해야 함| plus ", normalized)
        if part.strip(" .,!?\t")
    ]

    candidates: list[dict[str, str]] = []
    for part in parts:
        title = _make_title(part)
        candidates.append(
            {
                "title": title,
                "micro_step": _make_micro_step(part),
                "effort_level": "tiny",
            }
        )

    if not candidates:
        candidates = [
            {
                "title": title,
                "micro_step": micro_step,
                "effort_level": "tiny",
            }
            for title, micro_step in SAFETY_NET_ACTIONS
        ]

    return candidates[:limit]


def generate_smaller_step(text: str) -> dict[str, str]:
    base = text.strip()
    return {
        "title": "더 작게 시작하기",
        "micro_step": f"'{base[:40]}'와 관련해서 30초 안에 할 수 있는 첫 표시만 남기기",
        "effort_level": "nano",
    }


def _make_title(text: str) -> str:
    cleaned = text.strip()
    if len(cleaned) <= 24:
        return cleaned
    return f"{cleaned[:24].rstrip()}..."


def _make_micro_step(text: str) -> str:
    cleaned = text.strip()
    if any(keyword in cleaned for keyword in ["메일", "email", "이메일"]):
        return f"{cleaned} 관련 메일 제목 또는 첫 문장만 쓰기"
    if any(keyword in cleaned for keyword in ["자료", "발표", "문서"]):
        return f"{cleaned} 관련 빈 문서 만들고 제목만 적기"
    if any(keyword in cleaned for keyword in ["공유", "팀", "연락", "메시지"]):
        return f"{cleaned} 관련 공유 메시지 한 줄 초안 쓰기"
    return f"{cleaned}을 2분 안에 시작할 수 있는 첫 행동 하나만 하기"
