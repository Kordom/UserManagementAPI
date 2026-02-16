import base64

def basic_auth_header(username: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_first_registered_user_becomes_admin(client):
    r = client.post("/users", json={"username": "admin", "password": "password123"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True
    assert data["is_active"] is True


def test_second_user_is_not_admin(client):
    client.post("/users", json={"username": "admin", "password": "password123"})
    r = client.post("/users", json={"username": "bob", "password": "password123"})
    assert r.status_code == 201
    assert r.json()["is_admin"] is False


def test_basic_auth_allows_access_to_me(client):
    client.post("/users", json={"username": "admin", "password": "password123"})

    r = client.get("/users/me", headers=basic_auth_header("admin", "password123"))
    assert r.status_code == 200
    assert r.json()["username"] == "admin"


def test_inactive_user_cannot_authenticate(client):
    client.post("/users", json={"username": "admin", "password": "password123"})
    client.post("/users", json={"username": "bob", "password": "password123"})

    r = client.patch("/users/2/deactivate", headers=basic_auth_header("admin", "password123"))
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    r2 = client.get("/users/me", headers=basic_auth_header("bob", "password123"))
    assert r2.status_code == 401


def test_non_admin_cannot_list_users(client):
    client.post("/users", json={"username": "admin", "password": "password123"})
    client.post("/users", json={"username": "bob", "password": "password123"})

    r = client.get("/users", headers=basic_auth_header("bob", "password123"))
    assert r.status_code == 403


def test_admin_cannot_deactivate_self(client):
    client.post("/users", json={"username": "admin", "password": "password123"})

    r = client.patch("/users/1/deactivate", headers=basic_auth_header("admin", "password123"))
    assert r.status_code in (400, 403)