from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_routine_crud_flow(client: TestClient, auth_headers: dict[str, str]):
    create_response = client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={
            "title": "물 한 컵 마시기",
            "micro_step": "컵에 물을 따라 한 모금 마십니다.",
            "effort_level": "quiet",
            "is_active": True,
        },
    )

    assert create_response.status_code == 201
    routine = create_response.json()
    assert routine["title"] == "물 한 컵 마시기"
    assert routine["is_active"] is True

    list_response = client.get("/api/v1/routines", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/routines/{routine['id']}",
        headers=auth_headers,
        json={"is_active": False, "effort_level": "gentle"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False
    assert update_response.json()["effort_level"] == "gentle"

    delete_response = client.delete(f"/api/v1/routines/{routine['id']}", headers=auth_headers)
    assert delete_response.status_code == 204
    assert client.get("/api/v1/routines", headers=auth_headers).json() == []


def test_routine_ownership_is_enforced(client: TestClient, auth_headers: dict[str, str]):
    other_headers = register_and_login(client, email="routine-other@example.com")
    create_response = client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={"title": "메일 제목", "micro_step": "제목 한 줄 쓰기"},
    )
    routine_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/routines/{routine_id}",
        headers=other_headers,
        json={"is_active": False},
    )
    delete_response = client.delete(f"/api/v1/routines/{routine_id}", headers=other_headers)

    assert update_response.status_code == 403
    assert delete_response.status_code == 403


def test_active_routine_can_start_action(client: TestClient, auth_headers: dict[str, str]):
    create_response = client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={"title": "물 한 컵", "micro_step": "컵에 물을 따라 한 모금 마십니다."},
    )

    response = client.post(
        f"/api/v1/routines/{create_response.json()['id']}/start-action",
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["status"] == "active"
    assert response.json()["title"] == "물 한 컵"


def test_inactive_routine_cannot_start_action(client: TestClient, auth_headers: dict[str, str]):
    create_response = client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={
            "title": "메일 제목",
            "micro_step": "메일 제목만 쓰기",
            "is_active": False,
        },
    )

    response = client.post(
        f"/api/v1/routines/{create_response.json()['id']}/start-action",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "ROUTINE_INACTIVE"


def test_other_user_cannot_start_routine_action(
    client: TestClient,
    auth_headers: dict[str, str],
):
    other_headers = register_and_login(client, email="routine-start-other@example.com")
    create_response = client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={"title": "책상 3개", "micro_step": "책상 위 물건 3개만 옮기기"},
    )

    response = client.post(
        f"/api/v1/routines/{create_response.json()['id']}/start-action",
        headers=other_headers,
    )

    assert response.status_code == 403
