from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import SessionDep, require_admin
from app.core.security import generate_api_key, get_key_prefix, hash_api_key
from app.db.models import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyRead, ApiKeyUpdate

router = APIRouter(
    prefix="/admin/api-keys",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_api_key(body: ApiKeyCreate, session: SessionDep) -> ApiKeyCreated:
    raw_key = generate_api_key()
    api_key = ApiKey(
        name=body.name,
        key_prefix=get_key_prefix(raw_key),
        key_hash=hash_api_key(raw_key),
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)

    return ApiKeyCreated(**ApiKeyRead.model_validate(api_key).model_dump(), key=raw_key)


@router.get("")
async def list_api_keys(session: SessionDep) -> list[ApiKeyRead]:
    result = await session.scalars(select(ApiKey).order_by(ApiKey.id))
    return [ApiKeyRead.model_validate(api_key) for api_key in result]


@router.patch("/{key_id}")
async def update_api_key(key_id: int, body: ApiKeyUpdate, session: SessionDep) -> ApiKeyRead:
    api_key = await session.get(ApiKey, key_id)
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="키를 찾을 수 없습니다")

    api_key.is_active = body.is_active
    await session.commit()
    await session.refresh(api_key)

    return ApiKeyRead.model_validate(api_key)
