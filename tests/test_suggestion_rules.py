from app.services.suggestion.generator import RuleBasedSuggestionGenerator
from app.services.suggestion.micro_step_builder import make_micro_step, make_title
from app.services.suggestion.splitter import split_brain_dump


def test_split_brain_dump_uses_common_korean_connectors():
    parts = split_brain_dump("발표 준비해야 하고 교수님 메일 보내야 함. 또 팀 일정 공유")

    assert parts == ["발표 준비", "교수님 메일 보내야 함", "팀 일정 공유"]


def test_split_brain_dump_handles_attached_korean_connectors():
    parts = split_brain_dump(
        "프로젝트 발표 준비해야 하는데 자료 정리하고 교수님께 메일 보내고 팀원에게 일정 공유해야 함"
    )

    assert parts == [
        "프로젝트 발표 준비",
        "자료 정리",
        "교수님께 메일 보내",
        "팀원에게 일정 공유해야 함",
    ]


def test_rule_based_generator_splits_production_style_brain_dump():
    generator = RuleBasedSuggestionGenerator()
    suggestions = generator.generate_micro_steps(
        "프로젝트 발표 준비해야 하는데 자료 정리하고 교수님께 메일 보내고 팀원에게 일정 공유해야 함"
    )

    micro_steps = [suggestion["micro_step"] for suggestion in suggestions]

    assert "발표 자료 제목만 작성하기" in micro_steps
    assert "교수님께 질문 메일 초안 한 줄 쓰기" in micro_steps
    assert "팀원에게 일정 공유 메시지 초안 쓰기" in micro_steps
    assert all(suggestion["generation_type"] == "original" for suggestion in suggestions)


def test_rule_based_generator_splits_daily_life_brain_dump():
    generator = RuleBasedSuggestionGenerator()
    suggestions = generator.generate_micro_steps(
        "\ubc25\uba39\uace0 \uc57d\uba39\uace0 "
        "\uc54c\ubc14\uac14\ub2e4\uac00 \uc774\ub825\uc11c10\uac1c \uc81c\ucd9c"
    )

    micro_steps = [suggestion["micro_step"] for suggestion in suggestions]

    assert "\uba39\uc744 \uac83 \ud55c \uac00\uc9c0\ub9cc \uc815\ud558\uae30" in micro_steps
    assert "\uc57d\uacfc \ubb3c\uc744 \uba3c\uc800 \uaebc\ub0b4\uae30" in micro_steps
    assert (
        "\uc54c\ubc14 \uad00\ub828 \ub2e4\uc74c \uc77c\uc815 \ud558\ub098\ub9cc "
        "\ud655\uc778\ud558\uae30" in micro_steps
    )
    assert "\uc774\ub825\uc11c \ud30c\uc77c \ud558\ub098\ub9cc \uc5f4\uae30" in micro_steps
    assert all(suggestion["generation_type"] == "original" for suggestion in suggestions)


def test_micro_step_builder_uses_keyword_specific_actions():
    mail_step = "교수님께 질문 메일 초안 한 줄 쓰기"
    long_title = "아주 긴 발표 자료 정리하고 팀 일정 공유하..."

    assert make_micro_step("교수님 메일 보내기") == mail_step
    assert make_micro_step("발표 자료 만들기") == "발표 자료 제목만 작성하기"
    assert make_title("아주 긴 발표 자료 정리하고 팀 일정 공유하기") == long_title


def test_rule_based_generator_limits_suggestions():
    generator = RuleBasedSuggestionGenerator()
    suggestions = generator.generate_micro_steps(
        "하나, 둘, 셋, 넷, 다섯, 여섯",
        limit=3,
    )

    assert len(suggestions) == 3
    assert all(suggestion["effort_level"] == "tiny" for suggestion in suggestions)


def test_rule_based_generator_can_make_smaller_step():
    generator = RuleBasedSuggestionGenerator()
    smaller = generator.generate_smaller_steps("프로젝트 발표 자료 정리하기")

    assert 1 <= len(smaller) <= 3
    assert smaller[0]["micro_step"] == "발표 자료 파일만 열기"
    assert all(item["effort_level"] == "nano" for item in smaller)
