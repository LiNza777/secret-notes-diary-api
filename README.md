# Secret Notes API

API для безопасного личного дневника с JWT-авторизацией.

## Технологии
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Docker + docker-compose
- JWT (python-jose)

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