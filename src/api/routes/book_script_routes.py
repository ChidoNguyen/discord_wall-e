from fastapi import APIRouter

#models
from src.api.models.book_model import UnknownBook, UserDetails
#services
from src.api.services.book_script_services import find_service
book_script = APIRouter()

@book_script.get("/")
async def home():
    print("HomePagePlaceHolder")
    return {"message" : "homepage"}

@book_script.post("/whisperfind")
@book_script.post("/find")
async def find(search_query: UnknownBook, user: UserDetails):
    service_status = find_service(search_query=search_query,user=user)
    if service_status is not None:
        pass
    return None

@book_script.post("/find_hardmode")
async def find_hardmode(search_query: UnknownBook, user: UserDetails):
    return None

@book_script.post("/pick")
async def pick(search_query: UnknownBook, user: UserDetails):
    return None

@book_script.get("/catalog")
async def catalog() -> dict | None:
    return None