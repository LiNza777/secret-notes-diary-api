from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Request, Depends, HTTPException
from passlib.context import CryptContext
from data_base import get_db
from sqlalchemy.orm import Session
from models import User
from config import settings # Импортируем наши настройки

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Генератор JWT (для пропусков)
def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Забираем время жизни из конфига
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Забираем секрет и алгоритм из конфига
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
def get_password_hash(password):
    """Превращает пароль '12345' в нечитаемый хэш для сохранения в БД"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Проверяет, совпадает ли введенный пароль с хэшем из БД"""
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 1. Пытаемся достать токен из куки, которая прилетела с запросом
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Вы не вошли в систему")
    
    # 2. Отрезаем приставку "Bearer " (оставляем только сам токен)
    token = token.replace("Bearer ", "")
    
    try:
        # 3. Проверяем печать! Если кто-то изменил токен, тут будет ошибка
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Токен сломан")
            
    except JWTError:
        # Если время вышло (exp) или подпись не сошлась — отбраковываем
        raise HTTPException(status_code=401, detail="Токен недействителен или просрочен")
    
    # 4. Находим пользователя в базе (чтобы убедиться, что его не удалили 5 минут назад)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь больше не существует")
        
    return user