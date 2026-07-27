from sqlalchemy.orm import Session
from models import User, Note
from schemas import UserRegisterSchema, NoteCreateSchema, NoteUpdateSchema
from auth import get_password_hash, verify_password

# ==================== СЕРВИСЫ ПОЛЬЗОВАТЕЛЕЙ ====================

def get_user_by_username(db: Session, username: str) -> User | None:
    """Ищет пользователя по имя аккаунта."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: UserRegisterSchema) -> User:
    """Хэширует пароль и создает нового пользователя."""
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Проверяет логин и пароль."""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ==================== СЕРВИСЫ ЗАМЕТОК ====================

def get_user_notes(db: Session, owner_id: int) -> list[Note]:
    """Получает все заметки конкретного пользователя."""
    return db.query(Note).filter(Note.owner_id == owner_id).all()

def get_note_by_id(db: Session, note_id: int, owner_id: int) -> Note | None:
    """Получает заметку по ID, проверяя, принадлежит ли она пользователю."""
    return db.query(Note).filter(Note.id == note_id, Note.owner_id == owner_id).first()

def create_note(db: Session, note_data: NoteCreateSchema, owner_id: int) -> Note:
    """Создает новую заметку."""
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        owner_id=owner_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

def update_note(db: Session, db_note: Note, note_data: NoteUpdateSchema) -> Note:
    """Частично обновляет заметку (только переданные поля)."""
    update_data = note_data.model_dump(exclude_unset=True) # Забираем только то, что прислал клиент
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, db_note: Note) -> None:
    """Удаляет заметку."""
    db.delete(db_note)
    db.commit()