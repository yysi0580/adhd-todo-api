import re


def split_brain_dump(raw_text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", raw_text).strip()
    return [
        part.strip(" .,!?\t")
        for part in re.split(
            r"[,\n]| 그리고 | 하고 | 해야 하고 | 해야함|해야 함| plus ",
            normalized,
        )
        if part.strip(" .,!?\t")
    ]
