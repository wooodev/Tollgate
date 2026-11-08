from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.security import hash_api_key
from app.db.models import ApiKey


async def test_create_api_key_returns_raw_key_once(
    client: AsyncClient, admin_headers: dict[str, str], db_engine: AsyncEngine
):
    response = await client.post("/admin/api-keys", json={"name": "web"}, headers=admin_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "web"
    assert body["is_active"] is True
    assert body["key"].startswith(body["key_prefix"])

    async with AsyncSession(db_engine) as session:
        stored = await session.scalar(select(ApiKey).where(ApiKey.id == body["id"]))
    assert stored.key_hash == hash_api_key(body["key"])
    assert stored.key_hash != body["key"]


async def test_list_api_keys_hides_raw_key(client: AsyncClient, admin_headers: dict[str, str]):
    await client.post("/admin/api-keys", json={"name": "web"}, headers=admin_headers)
    await client.post("/admin/api-keys", json={"name": "batch"}, headers=admin_headers)

    response = await client.get("/admin/api-keys", headers=admin_headers)

    assert response.status_code == 200
    keys = response.json()
    assert [key["name"] for key in keys] == ["web", "batch"]
    assert all("key" not in key and "key_hash" not in key for key in keys)


async def test_deactivate_api_key(client: AsyncClient, admin_headers: dict[str, str]):
    created = await client.post("/admin/api-keys", json={"name": "web"}, headers=admin_headers)
    key_id = created.json()["id"]

    response = await client.patch(
        f"/admin/api-keys/{key_id}", json={"is_active": False}, headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    listed = await client.get("/admin/api-keys", headers=admin_headers)
    assert listed.json()[0]["is_active"] is False


async def test_deactivate_unknown_key_returns_404(
    client: AsyncClient, admin_headers: dict[str, str]
):
    response = await client.patch(
        "/admin/api-keys/9999", json={"is_active": False}, headers=admin_headers
    )

    assert response.status_code == 404


async def test_create_api_key_rejects_empty_name(
    client: AsyncClient, admin_headers: dict[str, str]
):
    response = await client.post("/admin/api-keys", json={"name": ""}, headers=admin_headers)

    assert response.status_code == 422


async def test_admin_endpoints_require_admin_token(client: AsyncClient):
    no_token = await client.get("/admin/api-keys")
    wrong_token = await client.get(
        "/admin/api-keys", headers={"Authorization": "Bearer wrong-token"}
    )

    assert no_token.status_code == 401
    assert wrong_token.status_code == 401
