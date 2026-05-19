from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_calendar_event_crud_and_ics_export(
    client: TestClient,
    auth_headers: dict[str, str],
):
    start_at = datetime(2026, 5, 19, 10, 0, tzinfo=UTC)
    end_at = start_at + timedelta(minutes=30)

    create_response = client.post(
        "/api/v1/calendar/events",
        headers=auth_headers,
        json={
            "title": "메일 첫 줄 쓰기",
            "description": "메일 창을 열고 첫 문장만 씁니다.",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        },
    )

    assert create_response.status_code == 201
    event = create_response.json()
    assert event["title"] == "메일 첫 줄 쓰기"
    assert event["source"] == "manual"
    assert event["external_uid"].startswith("adhd-todo-event-")

    list_response = client.get("/api/v1/calendar/events", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["id"] == event["id"] for item in list_response.json())

    ics_response = client.get("/api/v1/calendar/events.ics", headers=auth_headers)
    assert ics_response.status_code == 200
    assert ics_response.headers["content-type"].startswith("text/calendar")
    assert "BEGIN:VCALENDAR" in ics_response.text
    assert "SUMMARY:메일 첫 줄 쓰기" in ics_response.text


def test_calendar_event_can_be_created_from_action(
    client: TestClient,
    auth_headers: dict[str, str],
):
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={
            "session_id": _create_session(client, auth_headers),
            "title": "발표 자료 제목만 쓰기",
            "micro_step": "빈 문서를 열고 제목만 적습니다.",
        },
    )
    action = action_response.json()
    start_at = datetime(2026, 5, 19, 11, 0, tzinfo=UTC)

    response = client.post(
        "/api/v1/calendar/events",
        headers=auth_headers,
        json={
            "action_id": action["id"],
            "start_at": start_at.isoformat(),
            "end_at": (start_at + timedelta(minutes=25)).isoformat(),
        },
    )

    assert response.status_code == 201
    event = response.json()
    assert event["title"] == action["title"]
    assert event["description"] == action["micro_step"]
    assert event["source"] == "action"


def test_calendar_event_rejects_other_user_action(
    client: TestClient,
    auth_headers: dict[str, str],
):
    other_headers = register_and_login(client)
    other_session_id = _create_session(client, other_headers)
    other_action_response = client.post(
        "/api/v1/actions",
        headers=other_headers,
        json={
            "session_id": other_session_id,
            "title": "다른 사용자 액션",
            "micro_step": "보이면 안 됩니다.",
        },
    )
    other_action_id = other_action_response.json()["id"]
    start_at = datetime(2026, 5, 19, 12, 0, tzinfo=UTC)

    response = client.post(
        "/api/v1/calendar/events",
        headers=auth_headers,
        json={
            "action_id": other_action_id,
            "start_at": start_at.isoformat(),
            "end_at": (start_at + timedelta(minutes=30)).isoformat(),
        },
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACTION_FORBIDDEN"


def test_calendar_event_rejects_invalid_time_range(
    client: TestClient,
    auth_headers: dict[str, str],
):
    start_at = datetime(2026, 5, 19, 13, 0, tzinfo=UTC)

    response = client.post(
        "/api/v1/calendar/events",
        headers=auth_headers,
        json={
            "title": "시간 오류",
            "start_at": start_at.isoformat(),
            "end_at": start_at.isoformat(),
        },
    )

    assert response.status_code == 422


def _create_session(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/sessions",
        headers=headers,
        json={"context_note": "calendar test"},
    )
    assert response.status_code == 201
    return response.json()["id"]
