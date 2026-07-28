from pydantic import BaseModel, Field
from datetime import datetime

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length= 3, max_length= 10)
    password: str = Field(..., min_length= 8, max_length= 20)
class UserLoginSchema(BaseModel):
    username:str
    password:str
class NoteSchema(BaseModel):
    title: str = Field(..., min_length= 2, max_length= 100)
    content: str = Field(..., min_length= 2, max_length= 500)
class NoteUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=100)
    content: str | None = Field(None, min_length=2, max_length=500)
class NoteCreateSchema(NoteSchema):
    pass
class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    owner_id: int
    model_config = {"from_attributes": True}        