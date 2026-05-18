import ssl
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, MONGODB_DB_NAME
from database.models import Story, User

_client: AsyncIOMotorClient = None


async def connect_db():
    global _client
    if not MONGODB_URI:
        raise ValueError("Thieu MONGODB_URI trong file .env!")

    # Fix loi SSL handshake tren Python 3.10 + Windows
    _client = AsyncIOMotorClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,   # bo qua loi SSL cert
        serverSelectionTimeoutMS=30000,
    )

    database = _client[MONGODB_DB_NAME]
    await init_beanie(database=database, document_models=[User, Story])
    print(f"Da ket noi MongoDB -> '{MONGODB_DB_NAME}'")


async def close_db():
    global _client
    if _client:
        _client.close()