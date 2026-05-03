from fastapi.testclient import TestClient


def test_brain_dump_creates_session_and_suggestions(client: TestClient):
    response = client.post(
        "/api/v1/brain-dumps",
        json={
            "raw_text": (
                "프로젝트 발표 준비해야 하는데 자료도 정리해야 하고 "
                "교수님께 질문 메일도 보내야 하고 팀원한테 일정도 공유해야 함"
            )
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session"]["id"] > 0
    assert body["brain_dump"]["raw_text"]
    assert 2 <= len(body["suggestions"]) <= 5
    micro_steps = [suggestion["micro_step"] for suggestion in body["suggestions"]]
    assert "발표 자료 제목만 작성하기" in micro_steps
    assert "교수님께 질문 메일 초안 한 줄 쓰기" in micro_steps
    assert "팀원에게 일정 공유 메시지 초안 쓰기" in micro_steps


def test_brain_dump_uses_existing_session_when_session_id_is_given(client: TestClient):
    session_response = client.post("/api/v1/sessions", json={"context_note": "reuse me"})
    session_id = session_response.json()["id"]

    response = client.post(
        "/api/v1/brain-dumps",
        json={"session_id": session_id, "raw_text": "메일 보내기. 자료 열기"},
    )

    assert response.status_code == 201
    assert response.json()["session"]["id"] == session_id
