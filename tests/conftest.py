import os

# app 모듈을 import하기 전에 테스트 설정을 넣는다. 로컬 .env보다 우선한다.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://gateway:gateway@localhost:5432/gateway_test",
)
TEST_ADMIN_TOKEN = "test-admin-token"

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ADMIN_TOKEN"] = TEST_ADMIN_TOKEN

from collections.abc import AsyncIterator  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import make_url, text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

from app.db.models import Base  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402


async def _create_test_database_if_missing() -> None:
    url = make_url(TEST_DATABASE_URL)
    admin_engine = create_async_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with admin_engine.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    await admin_engine.dispose()


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    """테스트마다 테이블을 새로 만든다. 이벤트 루프가 테스트마다 달라 NullPool을 쓴다."""
    await _create_test_database_if_missing()
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def client(db_engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TEST_ADMIN_TOKEN}"}
