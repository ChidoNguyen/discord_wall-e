from fastapi import FastAPI
from api.routes.book_script_routes import book_script

app= FastAPI()
app.include_router(book_script)