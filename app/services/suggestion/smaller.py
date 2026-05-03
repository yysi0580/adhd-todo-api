def build_smaller_step(text: str) -> dict[str, str]:
    base = text.strip()
    return {
        "title": "더 작게 시작하기",
        "micro_step": f"'{base[:40]}'와 관련해서 30초 안에 할 수 있는 첫 표시만 남기기",
        "effort_level": "nano",
    }
