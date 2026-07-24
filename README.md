# Secret Notes API

REST API для хранения личных заметок с JWT-аутентификацией.
Каждый пользователь имеет собственное пространство заметок.
Поддерживаются регистрация, авторизация, CRUD операций над заметками, миграции базы данных и контейнеризация через Docker.



## Возможности

- регистрация пользователей
- JWT-аутентификация через HttpOnly Cookie
- CRUD заметок
- защита данных пользователя
- миграции Alembic
- Docker

## Особенности реализации

- JWT хранится в HttpOnly Cookie
- Пароли хэшируются bcrypt
- SQLAlchemy ORM
- Alembic для миграций
- Каждый пользователь имеет доступ только к собственным заметкам

## Технологии
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Docker + docker-compose
- JWT (python-jose)

## Архитектура

├── auth.py
├── config.py
├── data_base.py
├── main.py
├── models.py
├── routers_auth.py
├── routers_notes.py
├── schemas.py
├── services.py
├── alembic/
├── Dockerfile
└── docker-compose.yml

## Запуск

1. Клонируй репозиторий
2. Создай `.env` файл по образцу `.env.example`
3. Запусти:
```bash
docker-compose up --build
```
4. Документация доступна по адресу: `http://localhost:8000/docs`

## База данных
Связь таблиц «Один ко многим» (One-to-Many):
- `users` (id, username, hashed_password)
- `notes` (id, title, content, created_at, updated_at, owner_id → users.id)


## Эндпоинты

### Auth
- `POST /register` — регистрация
- `POST /login` — вход, возвращает JWT в куки
- `POST /logout` — выход

### Notes
- `GET /notes/` — все заметки текущего пользователя
- `POST /notes/` — создать заметку
- `GET /notes/{id}` — получить заметку
- `PUT /notes/{id}` — обновить заметку
- `DELETE /notes/{id}` — удалить заметку

## Безопасность
- Пароли хранятся в виде bcrypt хэша
- JWT токен хранится в httponly куки
- Каждый пользователь видит только свои заметки