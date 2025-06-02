from fastapi import APIRouter

#models
from src.api.models.book_model import UnknownBook, UserDetails
#services
from src.api.services.book_script_services import find_service, find_hardmode_service, pick_service, catalog_service
book_script = APIRouter()

@book_script.get("/")
async def home():
    print("HomePagePlaceHolder")
    return {"message" : "homepage"}

@book_script.post("/whisperfind")
@book_script.post("/find")
async def find(search_query: UnknownBook, user: UserDetails):
    return find_service(search_query=search_query,user=user)


@book_script.post("/find_hardmode")
async def find_hardmode(search_query: UnknownBook, user: UserDetails):
    return find_hardmode_service(search_query=search_query,user=user)

@book_script.post("/pick")
async def pick(search_query: UnknownBook, user: UserDetails):
    return pick_service(search_query=search_query,user=user)

@book_script.get("/catalog")
async def catalog():
    return catalog_service()

@book_script.post("/donezo")
async def done():
    return None