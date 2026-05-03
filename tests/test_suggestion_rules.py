from app.services.suggestion.generator import RuleBasedSuggestionGenerator
from app.services.suggestion.micro_step_builder import make_micro_step, make_title
from app.services.suggestion.splitter import split_brain_dump


def test_split_brain_dump_uses_common_korean_connectors():
    parts = split_brain_dump("발표 준비해야 하고 교수님 메일 보내야 함, 팀 일정 공유")

    assert parts == ["발표 준비해야", "교수님 메일 보내야 함", "팀 일정 공유"]


def test_micro_step_builder_uses_keyword_specific_actions():
    mail_step = "교수님 메일 보내기 관련 메일 제목 또는 첫 문장만 쓰기"
    long_title = "아주 긴 발표 자료 정리하고 팀 일정 공유하..."

    assert make_micro_step("교수님 메일 보내기") == mail_step
    assert make_micro_step("발표 자료 만들기") == "발표 자료 만들기 관련 빈 문서 만들고 제목만 적기"
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
    smaller = generator.generate_smaller_step("발표 자료 관련 빈 문서 만들고 제목만 적기")

    assert smaller["title"] == "더 작게 시작하기"
    assert smaller["effort_level"] == "nano"
