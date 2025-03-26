from fastapi import FastAPI
from .routes.routes import router as api_endpoints


app = FastAPI()
app.include_router(api_endpoints)
