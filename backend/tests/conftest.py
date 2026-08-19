import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-enough-entropy"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base, get_db
from app.main import app

engine = create_async_engine("sqlite+aiosqlite:///:memory:")
TestingSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_db():
    async with TestingSession() as session: yield session

app.dependency_overrides[get_db] = override_db

@pytest_asyncio.fixture(autouse=True)
async def database():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value: yield value

async def register(client, email="trader@example.com"):
    result = await client.post("/api/v1/auth/register", json={"name":"Trader","email":email,"password":"strongpass123"})
    return result, {"Authorization": f"Bearer {result.json()['access_token']}"}

@pytest_asyncio.fixture
async def auth(client):
    _, headers = await register(client); return headers

