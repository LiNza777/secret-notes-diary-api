from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import AsyncSession
from data_base import get_db
from schemas import NoteCreateSchema, NoteUpdateSchema, NoteResponse
from auth import get_current_user
from models import User
import services

notes_router = APIRouter(prefix="/notes", tags=["Notes"])


@notes_router.get("/", response_model=list[NoteResponse])
async def get_notes(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return await services.get_user_notes(db, owner_id=current_user.id)

@notes_router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreateSchema, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return await services.create_note(db, note_data, owner_id=current_user.id)

@notes_router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    return db_note

@notes_router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int, 
    note_data: NoteUpdateSchema, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """ Ищем заметку и сразу проверяем права доступа"""
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    
    """ Обновляем через сервис"""
    return await services.update_note(db, db_note, note_data)

@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Заметка не найдена"
        )
    
    await services.delete_note(db, db_note)
    return None