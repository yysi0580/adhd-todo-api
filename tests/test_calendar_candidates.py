from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_calendar_candidates_are_created_from_session_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id = _create_brain_dump_with_suggestions(client, auth_headers)

    response = client.post(
        "/api/v1/calendar/candidates/from-suggestions",
        headers=auth_headers,
        json={"session_id": session_id},
    )

    assert response.status_code == 201
    candidates = response.json()
    assert 2 <= len(candidates) <= 5
    assert all(item["estimated_minutes"] > 0 for item in candidates)
    assert all(item["status"] == "proposed" for item in candidates)
    assert all(item["session_id"] == session_id for item in candidates)


def test_calendar_candidate_can_be_scheduled_as_event(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id = _create_brain_dump_with_suggestions(client, auth_headers)
    candidate = client.post(
        "/api/v1/calendar/candidates/from-suggestions",
        headers=auth_headers,
        json={"session_id": session_id},
    ).json()[0]
    start_at = datetime(2026, 5, 20, 9, 0, tzinfo=UTC)

    response = client.post(
        f"/api/v1/calendar/candidates/{candidate['id']}/schedule",
        headers=auth_headers,
        json={
            "start_at": start_at.isoformat(),
            "end_at": (start_at + timedelta(minutes=30)).isoformat(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidate"]["status"] == "scheduled"
    assert body["event"]["title"] == candidate["title"]
    assert body["event"]["source"] == "calendar_candidate"


def test_calendar_candidate_rejects_other_user_session(
    client: TestClient,
    auth_headers: dict[str, str],
):
    other_headers = register_and_login(client)
    other_session_id = _create_brain_dump_with_suggestions(client, other_headers)

    response = client.post(
        "/api/v1/calendar/candidates/from-suggestions",
        headers=auth_headers,
        json={"session_id": other_session_id},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "SESSION_FORBIDDEN"


def test_calendar_candidate_cannot_schedule_twice(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id = _create_brain_dump_with_suggestions(client, auth_headers)
    candidate = client.post(
        "/api/v1/calendar/candidates/from-suggestions",
        headers=auth_headers,
        json={"session_id": session_id},
    ).json()[0]
    start_at = datetime(2026, 5, 20, 10, 0, tzinfo=UTC)
    payload = {
        "start_at": start_at.isoformat(),
        "end_at": (start_at + timedelta(minutes=20)).isoformat(),
    }

    first = client.post(
        f"/api/v1/calendar/candidates/{candidate['id']}/schedule",
        headers=auth_headers,
        json=payload,
    )
    second = client.post(
        f"/api/v1/calendar/candidates/{candidate['id']}/schedule",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["code"] == "CALENDAR_CANDIDATE_ALREADY_SCHEDULED"


def _create_brain_dump_with_suggestions(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/brain-dumps",
        headers=headers,
        json={
            "raw_text": (
                "\ubc25\uba39\uace0 \uc57d\uba39\uace0 "
                "\uc54c\ubc14\uac14\ub2e4\uac00 \uc774\ub825\uc11c10\uac1c \uc81c\ucd9c"
            )
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["suggestions"]) >= 2
    return body["session"]["id"]
