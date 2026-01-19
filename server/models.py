from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List

DataT = TypeVar('DataT')

class ApiResponse(BaseModel, Generic[DataT]):
    code: int
    message: str
    data: Optional[DataT] = None

class TaskCreate(BaseModel):
    name: str
    login_id: str
    password: str
    chat_id: str
    target_semester_code: Optional[str] = None
    interval: int = 300

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    login_id: Optional[str] = None
    password: Optional[str] = None
    chat_id: Optional[str] = None
    target_semester_code: Optional[str] = None
    interval: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    name: str
    login_id: str
    target_semester_code: Optional[str]
    interval: int
    status: str
    pid: Optional[int]
