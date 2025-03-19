from fastapi import APIRouter
from pydantic import BaseModel

from ..services import search_book

router = APIRouter()

class UnknownBook(BaseModel):
    title: str
    author: str
    username : str

@router.get("/")
async def home():
    print("Homepage")
    return {"message" : "homepage"}

@router.post("/find_book")
async def find_book(UnkBook : UnknownBook):
    book_info = UnkBook.model_dump()
    novel = await search_book(book_info)
    return {"message" : novel}