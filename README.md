API для хранения личных заметок с JWT-аутентификацией.
Каждый пользователь имеет собственное пространство заметок.
Поддерживаются регистрация, авторизация, CRUD-операции над заметками, миграции базы данных и контейнеризация через Docker.

## Ссылки
*  **Live Demo (Swagger UI):** [Перейти к документации](https://handsome-perfection-production-bcec.up.railway.app/docs)
  
<img width="1521" height="865" alt="swagger" src="https://github.com/user-attachments/assets/eeb1e633-4060-48a5-9b1e-61f5a5b04e3f" />

## Возможности и Безопасность

- Полностью асинхронный стек: Высокая производительность благодаря FastAPI, `AsyncSession` в SQLAlchemy и асинхронным драйверам БД.
- Защита от брутфорса (Rate Limiting): Ограничение количества запросов к эндпоинтам авторизации через `slowapi` с хранением счетчиков в Redis.
- Безопасная аутентификация (JWT): Токены передаются в защищенных `HttpOnly` и `SameSite` Cookie.
- Хэширование паролей: Безопасное хранение паролей с использованием алгоритма `bcrypt`.
- Изоляция данных: Каждый пользователь имеет доступ строго к собственным заметкам.
- Качество кода и стиль: Автоматическая проверка типов, сортировка импортов и форматирование кода с помощью Ruff.
- ORM и Миграции: SQLAlchemy 2.0 (Async) + автоматическое управление схемой через Alembic.
- CI/CD и Тестирование: Автоматический прогон асинхронных тестов (`pytest`) и линтеров при каждом Push/PR в GitHub Actions.
- Контейнеризация: Готовая конфигурация Docker + Docker Compose для разворачивания всей инфраструктуры одной командой.

## Технологии
* Фреймворк:FastAPI (Python 3.10+)
* База данных: PostgreSQL & Async SQLAlchemy 2.0
* Миграции: Alembic
* Кеширование и Rate Limiting: Redis & slowapi
* Аутентификация: PyJWT / python-jose, passlib (bcrypt)
* Линтинг и форматирование: Ruff
* Тестирование: Pytest, HTTPX, AsyncIO, Locust (нагрузочное тестирование)
* CI/CD: GitHub Actions
* Контейнеризация: Docker, Docker Compose

## Архитектура
```text

├── .github/              
│  └── workflows/         # Пайплайн CI/CD (GitHub Actions)
├── alembic/              # Миграции базы данных
├── assets                # Ассеты проекта
├── tests/                # Интеграционные асинхронные тесты (PyTest + HTTPX)
├── alembic.ini           # Конфигурация Alembic
├── auth.py               # Логика генерации JWT, проверки токенов и хэширования
├── base.py               # Базовый класс SQLAlchemy моделей (DeclarativeBase)
├── config.py             # Валидация env-переменных и конфигурация (Pydantic Settings)
├── data_base.py          # Инициализация асинхронного движка БД и сессий (AsyncSession)
├── Dockerfile            # Сборка Docker-образа приложения
├── docker-compose.yml    # Оркестрация сервисов (App + PostgreSQL + Redis)
├── .env.example          # Шаблон конфигурационного файла
├── limiter.py            # Инициализация Rate Limiter (slowapi)
├── locustfile.py         # Сценарии нагрузочного тестирования API
├── main.py               # Точка входа в приложение, подключение роутеров и мидлварей
├── models.py             # Асинхронные SQLAlchemy модели (User, Note)
├── pyproject.toml        # Конфигурация линтера и форматтера Ruff
├── pytest.ini            # Конфигурация тестов Pytest
├── redis_client.py       # Асинхронное подключение к Redis
├── requirements.txt      # Зависимости проекта
├── routers_auth.py       # Эндпоинты аутентификации, логина и выхода
├── routers_notes.py      # CRUD-эндпоинты для работы с заметками
├── schemas.py            # Pydantic схемы для валидации входных/выходных данных
└── services.py           # Асинхронная бизнес-логика и работа с БД
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
- `GET /auth/me`— получение профиля текущего пользователя
- `POST /auth/logout` — выход

### Notes
- `GET /notes/` — все заметки текущего пользователя
- `POST /notes/` — создать заметку
- `GET /notes/{id}` — получить заметку
- `PATCH /notes/{id}` — обновить заметку(частично)
- `DELETE /notes/{id}` — удалить заметку

## Тестирование

Тесты написаны с использованием pytest-asyncio и httpx. Во время прогона тестов Rate Limiter автоматически отключается для исключения внешней зависимости от Redis. 
Тесты покрывают жизненный цикл аутентификации: регистрацию, логин, проверку защищенных эндпоинтов и логаут.

### Запуск тестов

1. Убедитесь, что установлены тестовые зависимости:
   ```bash
   pip install pytest httpx
2. Запустите тесты из корневой директории проекта:
   ```bash
   python -m pytest -v

## Нагрузочное тестирование (Locust)

Для проверки производительности API и устойчивости облачной базы данных под высокими нагрузками используются сценарии Locust. Тесты имитируют поведение реальных пользователей: регистрацию, логин и активное взаимодействие с эндпоинтами (создание, чтение и удаление заметок).

### Запуск нагрузочных тестов
1. Убедитесь, что установлено необходимое ПО:
   ```bash
   pip install locust
2. Запустите Locust из корневой директории:
   ```bash
   locust -f locustfile.py
3. Откройте веб-интерфейс по адресу http://localhost:8080
4. Укажите параметры нагрузки и локальный URL API http://localhost:8000 или [ссылку на Railway](https://handsome-perfection-production-bcec.up.railway.app), чтобы запустить тест.

<img width="1488" height="900" alt="locus-report" src="https://github.com/user-attachments/assets/9b691fb0-16d8-4e8b-8e49-5a017ad42c3c" />

## Линтинг и форматирование (Ruff)
Для проверки и форматирования кода используется Ruff:![Результаты Locust](assets/locust-report.png)
- Проверка кода на ошибки и неиспользуемые импорты
```bash
   ruff check .
```
- Автоматическое форматирование кода
```bash
   ruff format .
