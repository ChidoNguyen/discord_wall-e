from fastapi import FastAPI
from api.routes.book_script_routes import book_script
#2XX - Responses 200 OK or 204 OK but no file
#4XX - API Errors
#5XX - SCRIPT Errors
app= FastAPI()
app.include_router(book_script)