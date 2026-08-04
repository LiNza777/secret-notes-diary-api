import pytest
from httpx import AsyncClient

async def test_register_user_success_async(client):
    """Тест 1: Успешная регистрация нового пользователя."""
    response = await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


async def test_register_duplicate_username_async(client):
    """Тест 2: Регистрация с уже занятым username должна возвращать 400."""
    await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Имя пользователя уже занято"


async def test_login_success_async(client):
    """Тест 3: Успешный вход должен возвращать 200 и устанавливать cookie access_token."""
    await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Успешный вход"}
    
    assert "access_token" in response.cookies


async def test_login_wrong_password_async(client):
    """Тест 4: Неверный пароль должен возвращать 401."""
    await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )

    response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"


async def test_get_me_unauthorized_async(client):
    """Тест 5: Запрос защищенного эндпоинта без авторизации должен возвращать 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_get_me_success_async(client):
    """Тест 6: Успешный доступ к защищенному эндпоинту с авторизованным клиентом."""
    await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )

    response = await client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


async def test_logout_async(client):
    """Тест 7: Логаут должен удалять куку авторизации."""
    await client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )

    logout_response = await client.post("/auth/logout")
    assert logout_response.status_code == 200
  
    me_response = await client.get("/auth/me")
    assert me_response.status_code == 401