from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from data_base import get_db
from schemas import UserRegisterSchema, UserLoginSchema
from auth import create_access_token, create_refresh_token, get_current_user, decode_token
from models import User
import services
import redis_client
from limiter import limiter

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

def send_welcome_email(username: str):
    print(f"[Background] Письмо отправлено пользователю: {username}")

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    form_data: UserRegisterSchema, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    if await services.get_user_by_username(db, form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Имя пользователя уже занято"
        )
    await services.create_user(db, form_data)
    background_tasks.add_task(send_welcome_email, form_data.username)
    return {"message": "Пользователь успешно зарегистрирован"}

@auth_router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: UserLoginSchema, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    user = await services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверное имя пользователя или пароль"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    await redis_client.save_refresh_token(
        user_id=user.username, 
        refresh_token=refresh_token,
        expire_seconds=604800
    )

    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True,
        samesite="lax",
        max_age=604800 
    )
    return {"message": "Успешный вход"}

@auth_router.post("/refresh")
async def refresh_tokens(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh токен отсутствует"
        )

    
    payload = decode_token(refresh_token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Некорректная структура токена"
        )

    if not await redis_client.is_refresh_token_valid(username, refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Токен отозван или срок его действия истек"
        )

    # Ротация токенов
    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    await redis_client.save_refresh_token(
        user_id=username, 
        refresh_token=new_refresh_token, 
        expire_seconds=604800
    )

    # Обновление куки
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {new_access_token}", 
        httponly=True, 
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True, 
        samesite="lax", 
        max_age=604800
    )

    return {"message": "Токены успешно обновлены"}

@auth_router.post("/logout")
async def logout(request: Request, response: Response):
    """Обычный выход: удаляет сессию текущего устройства из Redis и чистит куки."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            username = payload.get("sub")
            if username:
                await redis_client.revoke_refresh_token(user_id=username)
        except HTTPException:
            pass  # Если токен и так просрочен, то просто чистим куки

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Вы вышли из системы"}

@auth_router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}

@auth_router.post("/logout/all")
async def logout_all(response: Response, current_user: User = Depends(get_current_user)):
    """Выход со всех устройств."""
    await redis_client.revoke_refresh_token(user_id=current_user.username)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Успешный выход со всех устройств"}