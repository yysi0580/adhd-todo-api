from fastapi.testclient import TestClient


def test_select_suggestion_as_action(client: TestClient):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "문서 만들고 제목 정해야 함"},
    )
    dump_body = dump_response.json()
    session_id = dump_body["session"]["id"]
    suggestion_id = dump_body["suggestions"][0]["id"]

    action_response = client.post(
        "/api/v1/actions",
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )

    assert action_response.status_code == 201
    assert action_response.json()["status"] == "active"


def test_complete_action_endpoint_sets_status(client: TestClient):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "교수님 메일 보내야 함"},
    )
    dump_body = dump_response.json()
    action_response = client.post(
        "/api/v1/actions",
        json={
            "session_id": dump_body["session"]["id"],
            "suggestion_id": dump_body["suggestions"][0]["id"],
        },
    )
    action_id = action_response.json()["id"]

    complete_response = client.post(
        f"/api/v1/actions/{action_id}/complete",
        json={"note": "finished without pressure"},
    )

    assert complete_response.status_code == 200
    body = complete_response.json()
    assert body["status"] == "completed"
    assert body["completion_note"] == "finished without pressure"


def test_abort_action_endpoint_sets_status_and_reason(client: TestClient):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "발표 자료 정리하기"},
    )
    dump_body = dump_response.json()
    action_response = client.post(
        "/api/v1/actions",
        json={
            "session_id": dump_body["session"]["id"],
            "suggestion_id": dump_body["suggestions"][0]["id"],
        },
    )
    action_id = action_response.json()["id"]

    abort_response = client.post(
        f"/api/v1/actions/{action_id}/abort",
        json={"reason": "too large right now"},
    )

    assert abort_response.status_code == 200
    body = abort_response.json()
    assert body["status"] == "aborted"
    assert body["abort_reason"] == "too large right now"


def test_finished_action_cannot_be_changed_again(client: TestClient):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "팀 일정 공유"},
    )
    dump_body = dump_response.json()
    action_response = client.post(
        "/api/v1/actions",
        json={
            "session_id": dump_body["session"]["id"],
            "suggestion_id": dump_body["suggestions"][0]["id"],
        },
    )
    action_id = action_response.json()["id"]

    client.post(f"/api/v1/actions/{action_id}/complete")
    second_response = client.post(f"/api/v1/actions/{action_id}/abort")

    assert second_response.status_code == 400
