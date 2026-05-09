from fastapi import FastAPI

from backend.routers import chat, health


app = FastAPI(title="ChatLab API")

app.include_router(health.router)
app.include_router(chat.router)
