def build_micro_step(text: str) -> dict[str, str]:
    return {
        "title": make_title(text),
        "micro_step": make_micro_step(text),
        "effort_level": "tiny",
    }


def make_title(text: str) -> str:
    cleaned = text.strip()
    if len(cleaned) <= 24:
        return cleaned
    return f"{cleaned[:24].rstrip()}..."


def make_micro_step(text: str) -> str:
    cleaned = text.strip()
    lowered = cleaned.lower()
    if "발표" in cleaned and any(keyword in cleaned for keyword in ["자료", "준비"]):
        return "발표 자료 제목만 작성하기"
    if "교수" in cleaned and any(keyword in cleaned for keyword in ["메일", "email", "이메일"]):
        return "교수님께 질문 메일 초안 한 줄 쓰기"
    if any(keyword in cleaned for keyword in ["팀원", "팀"]) and any(
        keyword in cleaned for keyword in ["일정", "공유", "메시지"]
    ):
        return "팀원에게 일정 공유 메시지 초안 쓰기"
    if any(keyword in cleaned for keyword in ["약", "복용"]):
        return "약과 물을 먼저 꺼내기"
    if any(keyword in cleaned for keyword in ["밥", "식사", "끼니"]):
        return "먹을 것 한 가지만 정하기"
    if any(keyword in cleaned for keyword in ["이력서", "지원서", "자소서", "자기소개서"]):
        return "이력서 파일 하나만 열기"
    if any(keyword in cleaned for keyword in ["알바", "출근", "근무"]):
        return "알바 관련 다음 일정 하나만 확인하기"
    if any(keyword in cleaned for keyword in ["메일", "email", "이메일"]):
        return f"{cleaned} 관련 메일 제목 또는 첫 문장만 쓰기"
    if any(keyword in cleaned for keyword in ["자료", "발표", "문서"]):
        return f"{cleaned} 관련 빈 문서 만들고 제목만 적기"
    if any(keyword in cleaned for keyword in ["공유", "팀", "연락", "메시지"]):
        return f"{cleaned} 관련 공유 메시지 한 줄 초안 쓰기"
    if any(keyword in lowered for keyword in ["open", "file"]):
        return f"{cleaned}을 열고 제목만 확인하기"
    return f"{cleaned}을 2분 안에 시작할 수 있는 첫 행동 하나만 하기"
