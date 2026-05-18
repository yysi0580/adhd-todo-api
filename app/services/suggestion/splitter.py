import re

MIN_PART_LENGTH = 3
NOISE_WORDS = {
    "그리고",
    "또",
    "먼저",
    "해야",
    "해야함",
    "해야 함",
    "해야 하고",
}

SPLIT_PATTERN = re.compile(
    r"""
    [,;\n]+
    |[.!?。]+
    |\s+그리고\s+
    |\s+또\s+
    |\s+먼저\s+
    |해야\s+하고\s+
    |해야하고\s+
    |해야\s+하는데\s+
    |해야하는데\s+
    |\s+하고\s+
    |(?<=\S)하고\s+
    |(?<=보내)고\s+
    |\s+plus\s+
    """,
    re.VERBOSE,
)


def split_brain_dump(raw_text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", raw_text).strip()
    parts = []
    for raw_part in SPLIT_PATTERN.split(normalized):
        part = _clean_part(raw_part)
        if _is_meaningful(part):
            parts.append(part)
    return parts


def _clean_part(part: str) -> str:
    return part.strip(" .,!?\t")


def _is_meaningful(part: str) -> bool:
    compact = part.replace(" ", "")
    if len(compact) < MIN_PART_LENGTH:
        return False
    return compact not in {word.replace(" ", "") for word in NOISE_WORDS}
