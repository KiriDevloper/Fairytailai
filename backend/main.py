from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config   import APP_HOST, APP_PORT, OUTPUT_DIR
from database import connect_db, close_db
from routers  import story_router, health_router
from routers.auth_router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title       = "Fairytale AI",
    description = "Tao video ke chuyen co tich tu text",
    version     = "1.0.0",
    lifespan    = lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(story_router)


@app.get("/")
def root():
    return {"message": "Fairytale AI API dang chay", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)