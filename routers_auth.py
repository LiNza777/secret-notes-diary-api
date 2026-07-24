from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from data_base import get_db
from models import User
from auth import get_current_user, verify_password, create_access_token, get_password_hash
from schemas import UserLoginSchema, UserRegisterSchema 

auth_router = APIRouter(tags=["auth"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(form_data: UserRegisterSchema, db: Session = Depends(get_db)):
    # Проверяем, существует ли уже такой юзер
    if db.query(User).filter(User.username == form_data.username).first():
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    # Хэшируем пароль и сохраняем
    new_user = User(
        username=form_data.username,
        hashed_password=get_password_hash(form_data.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Пользователь успешно зарегистрирован"}

@auth_router.post("/login")
def login(response: Response, form_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800
    )
    return {"message": "Успешный вход"}
@auth_router.post(
    "/logout",
    summary="Выход из системы",
    description="Очищает авторизационные куки и завершает сессию текущего пользователя."
)
def logout(
    response: Response, 
    current_user: User = Depends(get_current_user)  # <-- Защищаем эндпоинт
):
    # Удаляем куку access_token
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False
    )
    
    return {
        "status": "success",
        "message": f"Пользователь {current_user.username} успешно вышел из системы"
    }