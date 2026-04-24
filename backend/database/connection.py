from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, MONGODB_DB_NAME
from database.models import Story

_client: AsyncIOMotorClient = None


async def connect_db():
    global _client
    if not MONGODB_URI:
        raise ValueError("Thieu MONGODB_URI trong file .env!")

    _client   = AsyncIOMotorClient(MONGODB_URI)
    database  = _client[MONGODB_DB_NAME]
    await init_beanie(database=database, document_models=[Story])
    print(f"Da ket noi MongoDB Atlas -> database: '{MONGODB_DB_NAME}'")


async def close_db():
    global _client
    if _client:
        _client.close()
        print("Da dong ket noi MongoDB.")