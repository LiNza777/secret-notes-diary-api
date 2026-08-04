from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash, verify_password
from models import Note, User
from schemas import NoteCreateSchema, NoteUpdateSchema, UserRegisterSchema

# ==================== СЕРВИСЫ ПОЛЬЗОВАТЕЛЕЙ ====================


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Ищет пользователя по имени аккаунта."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRegisterSchema) -> User:
    """Хэширует пароль и создает нового пользователя."""
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """Проверяет логин и пароль."""
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ==================== СЕРВИСЫ ЗАМЕТОК ====================


async def get_user_notes(db: AsyncSession, owner_id: int) -> list[Note]:
    """Получает все заметки конкретного пользователя."""
    result = await db.execute(select(Note).where(Note.owner_id == owner_id))
    return result.scalars().all()


async def get_note_by_id(db: AsyncSession, note_id: int, owner_id: int) -> Note | None:
    """Получает заметку по ID, проверяя, принадлежит ли она пользователю."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def create_note(
    db: AsyncSession, note_data: NoteCreateSchema, owner_id: int
) -> Note:
    """Создает новую заметку."""
    new_note = Note(title=note_data.title, content=note_data.content, owner_id=owner_id)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


async def update_note(
    db: AsyncSession, db_note: Note, note_data: NoteUpdateSchema
) -> Note:
    """Частично обновляет заметку (только переданные поля)."""
    update_data = note_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)

    await db.commit()
    await db.refresh(db_note)
    return db_note


async def delete_note(db: AsyncSession, db_note: Note) -> None:
    """Удаляет заметку."""
    await db.delete(db_note)
    await db.commit()
