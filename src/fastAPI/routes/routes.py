from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict , Any
from ..services import find_book_service , find_book_service_roids
#### Routes - > Input validation / Handlings #####
router = APIRouter()

class UnknownBook(BaseModel):
    title: str
    author: str

class UserDetails(BaseModel):
    username : str

@router.get("/")
async def home():
    print("Homepage")
    return {"message" : "homepage"}


##### Move to util function later??######
### notes to self : create "bookboterror" in sel script

def template_api_response(status: str, message: str, data : Dict[str,Any] | None, error_details : Dict[str,str] | None):
    response = {
        "status" : status,
        "message" : message,
        "data" : data if data else {}
    }
    
    if error_details:
        response['error_details'] = error_details

    return response
@router.post("/find_book")
async def find_book(unknown_book : UnknownBook, user_details : UserDetails):
    #print("looking")
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_book_service(book_info,user_info)
    #print(novel)
    if novel is not None:
        return {"message" : novel}
    return None

@router.post("/find_book_roids")
async def find_book_roids(unknown_book : UnknownBook, user_details : UserDetails):
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_book_service_roids(book_info,user_info)
    #print(novel)
    if novel is not None:
        return {"message" : novel}
    return None

@router.post("/pick")
async def pick_book():
    return "done"