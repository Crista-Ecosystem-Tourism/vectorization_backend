from fastapi import FastAPI
from app.api.v1 import search

app = FastAPI()
app.include_router(search.router, prefix="/api/v1")
