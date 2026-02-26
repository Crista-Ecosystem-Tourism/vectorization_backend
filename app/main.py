from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import search, load_data

app = FastAPI()

# CORS — разрешаем запросы от ai_agent и фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")
app.include_router(load_data.router, prefix="/api/v1")
