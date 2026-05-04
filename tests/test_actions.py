from conftest import register_and_login
from fastapi.testclient import TestClient


def _create_suggestion(client: TestClient, headers: dict[str, str]) -> tuple[int, int]:
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=headers,
        json={"raw_text": "문서 만들고 제목 정해야 함"},
    )
    dump_body = dump_response.json()
    return dump_body["session"]["id"], dump_body["suggestions"][0]["id"]


def test_select_suggestion_as_action(client: TestClient, auth_headers: dict[str, str]):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)

    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )

    assert action_response.status_code == 201
    body = action_response.json()
    assert body["status"] == "active"
    assert body["suggestion_id"] == suggestion_id
    assert body["title"]
    assert body["micro_step"]


def test_read_action_endpoint_returns_owned_action(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    action_id = action_response.json()["id"]

    read_response = client.get(f"/api/v1/actions/{action_id}", headers=auth_headers)

    assert read_response.status_code == 200
    assert read_response.json()["id"] == action_id
    assert read_response.json()["status"] == "active"


def test_other_user_cannot_read_action(client: TestClient, auth_headers: dict[str, str]):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    other_headers = register_and_login(client)

    response = client.get(
        f"/api/v1/actions/{action_response.json()['id']}",
        headers=other_headers,
    )

    assert response.status_code == 403


def test_duplicate_action_for_same_suggestion_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    payload = {"session_id": session_id, "suggestion_id": suggestion_id}

    assert client.post("/api/v1/actions", headers=auth_headers, json=payload).status_code == 201
    duplicate_response = client.post("/api/v1/actions", headers=auth_headers, json=payload)

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["code"] == "DUPLICATE_ACTION_FOR_SUGGESTION"


def test_complete_action_endpoint_sets_status(client: TestClient, auth_headers: dict[str, str]):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    action_id = action_response.json()["id"]

    complete_response = client.post(
        f"/api/v1/actions/{action_id}/complete",
        headers=auth_headers,
        json={"note": "finished without pressure"},
    )

    assert complete_response.status_code == 200
    body = complete_response.json()
    assert body["status"] == "completed"
    assert body["completion_note"] == "finished without pressure"


def test_abort_action_endpoint_sets_status_and_reason(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    action_id = action_response.json()["id"]

    abort_response = client.post(
        f"/api/v1/actions/{action_id}/abort",
        headers=auth_headers,
        json={"reason": "too large right now"},
    )

    assert abort_response.status_code == 200
    body = abort_response.json()
    assert body["status"] == "aborted"
    assert body["abort_reason"] == "too large right now"


def test_finished_action_cannot_be_changed_again(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    action_id = action_response.json()["id"]

    client.post(f"/api/v1/actions/{action_id}/complete", headers=auth_headers)
    second_response = client.post(f"/api/v1/actions/{action_id}/abort", headers=auth_headers)

    assert second_response.status_code == 400
    assert second_response.json()["code"] == "ACTION_ALREADY_FINISHED"


def test_aborted_action_cannot_be_completed(client: TestClient, auth_headers: dict[str, str]):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    action_id = action_response.json()["id"]

    client.post(f"/api/v1/actions/{action_id}/abort", headers=auth_headers)
    second_response = client.post(f"/api/v1/actions/{action_id}/complete", headers=auth_headers)

    assert second_response.status_code == 400
    assert second_response.json()["code"] == "ACTION_ALREADY_FINISHED"


def test_patch_action_endpoint_is_removed(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/api/v1/actions/1",
        headers=auth_headers,
        json={"status": "completed"},
    )

    assert response.status_code in {404, 405}


def test_other_user_cannot_access_action(client: TestClient, auth_headers: dict[str, str]):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    action_response = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )
    other_headers = register_and_login(client)

    response = client.post(
        f"/api/v1/actions/{action_response.json()['id']}/complete",
        headers=other_headers,
    )

    assert response.status_code == 403
