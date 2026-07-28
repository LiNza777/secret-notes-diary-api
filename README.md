# Secret Notes API

REST API для хранения личных заметок с JWT-аутентификацией.
Каждый пользователь имеет собственное пространство заметок.
Поддерживаются регистрация, авторизация, CRUD-операции над заметками, миграции базы данных и контейнеризация через Docker.

## Ссылки
*  **Live Demo (Swagger UI):** [Перейти к документации](https://secret-notes-diary-api-production.up.railway.app/docs)

## Возможности и Безопасность

- Регистрация и авторизация пользователей
- JWT-аутентификация через безопасные `HttpOnly` Cookie
- Хэширование паролей с помощью `bcrypt`
- Изоляция данных: каждый пользователь имеет доступ только к своим заметкам
- SQLAlchemy ORM
- Автоматические миграции базы данных через Alembic
- Полная контейнеризация приложения (Docker + Compose)


## Технологии
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Docker + docker-compose
- JWT (python-jose)

## Архитектура
```text
├── alembic/              # Миграции базы данных
├── auth.py               # Логика аутентификации и работы с токенами
├── config.py             # Настройки приложения и валидация env-переменных
├── data_base.py          # Инициализация БД и создание сессий
├── Dockerfile            # Инструкция для сборки образа приложения
├── docker-compose.yml    # Оркестрация контейнеров (App + DB)
├── .env.example          # Шаблон конфигурационного файла
├── main.py               # Точка входа в приложение
├── models.py             # SQLAlchemy модели (User, Note)
├── routers_auth.py       # Эндпоинты для регистрации и авторизации
├── routers_notes.py      # Эндпоинты для работы с заметками
├── schemas.py            # Pydantic схемы для валидации данных
└── services.py           # Бизнес-логика приложения
```

## Запуск проекта

1. Клонируйте репозиторий:
   ```bash
   git clone <url_репозитория>
   cd secret-notes-api
   ```
2. Создайте файл `.env` на основе шаблона и заполните его своими данными:
   ```bash
   cp .env.example .env
   ```
3. Запустите проект в Docker:
   ```bash
   docker compose up --build
   ```
4. Примените миграции для создания таблиц в базе данных:
    ```bash
    docker compose exec app alembic upgrade head
    ```
5. Интерактивная документация API (Swagger) будет доступна по адресу: `http://localhost:8000/docs`

## База данных
Связь таблиц «Один ко многим» (One-to-Many):
- `users` (id, username, hashed_password)
- `notes` (id, title, content, created_at, updated_at, owner_id → users.id)


## Эндпоинты

### Auth
- `POST /auth/register` — регистрация
- `POST /auth/login` — вход, возвращает JWT в куки
- `POST /auth/logout` — выход

### Notes
- `GET /notes/` — все заметки текущего пользователя
- `POST /notes/` — создать заметку
- `GET /notes/{id}` — получить заметку
- `PATCH /notes/{id}` — обновить заметку
- `DELETE /notes/{id}` — удалить заметку