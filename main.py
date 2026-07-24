from fastapi import FastAPI
from routers_auth import auth_router 
from routers_notes import notes_router     



# 2. Инициализируем приложение
app = FastAPI(
    title="Secret Notes API",
    description="API для безопасного дневника с JWT-авторизацией",
    version="1.0.0"
)

# 3. Подключаем наши роутеры (модули с эндпоинтами)
# auth_router отвечает за регистрацию и логин
# notes_router отвечает за операции с заметками
app.include_router(auth_router)
app.include_router(notes_router)

# Стартовый эндпоинт для проверки связи
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API работает успешно!", 
        "docs": "Перейди по адресу /docs, чтобы протестировать эндпоинты"
    }