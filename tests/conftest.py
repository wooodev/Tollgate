import os

# app 모듈을 import하기 전에 테스트 설정을 넣는다. 로컬 .env보다 우선한다.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://gateway:gateway@localhost:5432/gateway_test",
)
TEST_ADMIN_TOKEN = "test-admin-token"

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ADMIN_TOKEN"] = TEST_ADMIN_TOKEN
