from fastapi import FastAPI
from routers_auth import auth_router 
from routers_notes import notes_router     

app = FastAPI(
    title="Secret Notes API",
    description="API для безопасного дневника с JWT-авторизацией",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API работает успешно!", 
        "docs": "Перейди по адресу /docs, чтобы протестировать эндпоинты"
    }