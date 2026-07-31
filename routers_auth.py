from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks
from sqlalchemy.orm import Session
from data_base import get_db
from schemas import UserRegisterSchema, UserLoginSchema
from auth import create_access_token, create_refresh_token, get_current_user, settings
from models import User
import services
import redis_client

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

def send_welcome_email(username: str):
    print(f"[Background] Письмо отправлено пользователю: {username}")

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(form_data: UserRegisterSchema,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if services.get_user_by_username(db, form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Имя пользователя уже занято"
        )
    services.create_user(db, form_data)
    background_tasks.add_task(send_welcome_email, form_data.username)
    return {"message": "Пользователь успешно зарегистрирован"}

@auth_router.post("/login")
def login(form_data: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    user = services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверное имя пользователя или пароль"
        )
    
    """Генерируем токен и кладем в HttpOnly cookie """
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    redis_client.save_refresh_token(
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
def refresh_tokens(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh токен отсутствует"
        )

    # 2. Расшифровываем JWT и достаем юзера
    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невалидный токен"
        )
    
    username = payload.get("sub")

    # 3. ПРОВЕРКА В REDIS: не был ли токен отозван через /logout
    if not redis_client.is_refresh_token_valid(username, refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Токен отозван или срок его действия истек"
        )

    # 4. Ротация токенов: создаем новую пару
    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    # 5. Перезаписываем старый токен в Redis новым
    redis_client.save_refresh_token(
        user_id=username, 
        refresh_token=new_refresh_token, 
        expire_seconds=604800
    )

    # 6. Обновляем куки в браузере
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
def logout(response: Response):
    """Очищаем куку при выходе"""
    response.delete_cookie("access_token")
    return {"message": "Вы вышли из системы"}

@auth_router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}

@auth_router.post("/logout/all")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    redis_client.revoke_refresh_token(user_id=current_user.username)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Успешный выход со всех устройств"}