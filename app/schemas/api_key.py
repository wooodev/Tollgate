from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ApiKeyUpdate(BaseModel):
    is_active: bool


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime


class ApiKeyCreated(ApiKeyRead):
    """발급 응답. 키 원문(key)은 이 응답에서만 한 번 노출된다."""

    key: str
