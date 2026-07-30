def test_register_user_success(client):
    """Тест 1: Успешная регистрация нового пользователя."""
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


def test_register_duplicate_username(client):
    """Тест 2: Регистрация с уже занятым username должна возвращать 400."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Имя пользователя уже занято"


def test_login_success(client):
    """Тест 3: Успешный вход должен возвращать 200 и устанавливать cookie access_token."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Успешный вход"}
    
    assert "access_token" in response.cookies


def test_login_wrong_password(client):
    """Тест 4: Неверный пароль должен возвращать 401."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"


def test_get_me_unauthorized(client):
    """Тест 5: Запрос защищенного эндпоинта без авторизации должен возвращать 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_success(client):
    """Тест 6: Успешный доступ к защищенному эндпоинту с авторизованным клиентом."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )

    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_logout(client):
    """Тест 7: Логаут должен удалять куку авторизации."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200
  
    me_response = client.get("/auth/me")
    assert me_response.status_code == 401