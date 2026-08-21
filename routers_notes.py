from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import services
from auth import get_current_user
from data_base import get_db
from models import User
from schemas import NoteCreateSchema, NoteResponse, NoteUpdateSchema
from services_llm import generate_note_summary

notes_router = APIRouter(prefix="/notes", tags=["Notes"])


@notes_router.get("/", response_model=list[NoteResponse])
async def get_notes(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await services.get_user_notes(db, owner_id=current_user.id)


@notes_router.post(
    "/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED
)
async def create_note(
    note_data: NoteCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await services.create_note(db, note_data, owner_id=current_user.id)


@notes_router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заметка не найдена"
        )
    return db_note


@notes_router.post("/{note_id}/summary", response_model=NoteResponse)
async def summarize_note(
    note_id: int,
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заметка не найдена"
        )
    if db_note.ai_summary and not force_refresh:
        return db_note

    summary = await generate_note_summary(db_note.content)

    db_note.ai_summary = summary
    await db.commit()
    await db.refresh(db_note)
    return db_note


@notes_router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заметка не найдена"
        )

    """ Обновляем через сервис"""
    return await services.update_note(db, db_note, note_data)


@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_note = await services.get_note_by_id(db, note_id, owner_id=current_user.id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заметка не найдена"
        )

    await services.delete_note(db, db_note)
    return None
