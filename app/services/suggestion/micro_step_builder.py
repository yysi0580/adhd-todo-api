def build_micro_step(text: str) -> dict[str, str]:
    return {
        "title": make_title(text),
        "micro_step": make_micro_step(text),
        "effort_level": "tiny",
    }


def build_smaller_step(text: str) -> dict[str, str]:
    base = text.strip()
    return {
        "title": "더 작게 시작하기",
        "micro_step": f"'{base[:40]}'와 관련해서 30초 안에 할 수 있는 첫 표시만 남기기",
        "effort_level": "nano",
    }


def make_title(text: str) -> str:
    cleaned = text.strip()
    if len(cleaned) <= 24:
        return cleaned
    return f"{cleaned[:24].rstrip()}..."


def make_micro_step(text: str) -> str:
    cleaned = text.strip()
    if any(keyword in cleaned for keyword in ["메일", "email", "이메일"]):
        return f"{cleaned} 관련 메일 제목 또는 첫 문장만 쓰기"
    if any(keyword in cleaned for keyword in ["자료", "발표", "문서"]):
        return f"{cleaned} 관련 빈 문서 만들고 제목만 적기"
    if any(keyword in cleaned for keyword in ["공유", "팀", "연락", "메시지"]):
        return f"{cleaned} 관련 공유 메시지 한 줄 초안 쓰기"
    return f"{cleaned}을 2분 안에 시작할 수 있는 첫 행동 하나만 하기"
