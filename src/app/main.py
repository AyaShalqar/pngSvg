from fastapi import FastAPI

from src.app.routes.script_routes import router

app = FastAPI()
app.include_router(router, prefix="/api")
