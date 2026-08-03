from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from data_base import get_db
from schemas import UserRegisterSchema, UserLoginSchema
from auth import create_access_token, get_current_user
from models import User
import services

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

async def send_welcome_email(username: str):
    print(f"[Background] Письмо отправлено пользователю: {username}")

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(form_data: UserRegisterSchema, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if await services.get_user_by_username(db, form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Имя пользователя уже занято"
        )
    await services.create_user(db, form_data)
    background_tasks.add_task(send_welcome_email, form_data.username)
    return {"message": "Пользователь успешно зарегистрирован"}

@auth_router.post("/login")
async def login(form_data: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    user = await services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверное имя пользователя или пароль"
        )
    
    """Генерируем токен и кладем в HttpOnly cookie """
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        samesite="lax"
    )
    return {"message": "Успешный вход"}

@auth_router.post("/logout")
async def logout(response: Response):
    """Очищаем куку при выходе"""
    response.delete_cookie("access_token")
    return {"message": "Вы вышли из системы"}

@auth_router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}