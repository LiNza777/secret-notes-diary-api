from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from data_base import get_db
from schemas import NoteCreateSchema, NoteUpdateSchema, NoteResponse
from auth import get_current_user
from models import User
import services

notes_router = APIRouter(prefix="/notes", tags=["Notes"])


@notes_router.get("/", response_model=list[NoteResponse])
def get_notes(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return services.get_user_notes(db, owner_id=current_user.id)

@notes_router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreateSchema, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return services.create_note(db, note_data, owner_id=current_user.id)

@notes_router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int, 
    note_data: NoteUpdateSchema, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Ищем заметку и сразу проверяем права доступа
    db_note = services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    
    # 2. Обновляем через сервис
    return services.update_note(db, db_note, note_data)

@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_note = services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    
    services.delete_note(db, db_note)
    return None
@notes_router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_note = services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    return db_note