from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from data_base import get_db
from models import Note, User
from auth import get_current_user
# Предположим, у тебя есть схемы для валидации данных
from schemas import NoteCreateSchema, NoteResponse 

notes_router = APIRouter(prefix="/notes", tags=["notes"])

@notes_router.get("/", response_model=List[NoteResponse])
def get_all_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 10):
    # Возвращаем только заметки текущего пользователя
    return db.query(Note).filter(Note.owner_id == current_user.id).offset(skip).limit(limit).all()

@notes_router.get("/{note_id}", response_model=NoteResponse)
def get_one_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    # ПРОВЕРКА: может ли пользователь видеть эту заметку?
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    return note

@notes_router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note_in: NoteCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_note = Note(**note_in.model_dump(), owner_id=current_user.id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note
@notes_router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_in: NoteCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Обновляем поля заметки
    note.title = note_in.title
    note.content = note_in.content
    
    # SQLAlchemy автоматически обновит поле updated_at, 
    # если в модели Note у колонки стоит onupdate=datetime.utcnow
    db.commit()
    db.refresh(note)
    return note

@notes_router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    db.delete(note)
    db.commit()
    return {"message": "Заметка удалена"}