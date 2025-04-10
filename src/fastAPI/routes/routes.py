from fastapi import APIRouter , BackgroundTasks
from pydantic import BaseModel
from typing import Dict , Any , Union
import json
from ..services import find_book_service , find_book_service_roids, find_book_options , to_the_vault , cron_fake

#### Routes - > Input validation / Handlings #####
router = APIRouter()

class UnknownBook(BaseModel):
    title: str
    author : Union[None,str] = ""
    #author: str = "" # want to show author option in book bot but make it optional

class UserDetails(BaseModel):
    username : str

@router.get("/")
async def home():
    print("Homepage")
    return {"message" : "homepage"}

@router.post("/find_book")
async def find_book(unknown_book : UnknownBook, user_details : UserDetails, background_tasks : BackgroundTasks):
    #print("looking")
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_book_service(book_info,user_info)
    #print(novel)
    '''
    Novel should be full JSON output could probably parse out meta data in "services" but for now skeleton it here
    '''
    ###
    # _ , _ values are steps and misc for debugging if needed
    req_status , job_json_data , message , _ , _ = novel.values()
    #can narrow down check on novel for extra check but services already check that status is success
    ###
    if novel is not None:
        background_tasks.add_task(cron_fake,job_json_data)
        return {"message" : 'acquired'}
    return None

@router.post("/find_book_roids")
async def find_book_roids(unknown_book : UnknownBook, user_details : UserDetails,background_tasks : BackgroundTasks):
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_book_service_roids(book_info,user_info)
    if novel is not None:
        return {"message" : 'found some stuff'}
    return None

@router.post("/pick")
async def pick_book(unknown_book : UnknownBook, user_details: UserDetails,background_tasks: BackgroundTasks):
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_book_options(book_info,user_info)
    _ , job_json_data , _ , _ , _ = novel.values()
    if novel is not None:
        background_tasks.add_task(cron_fake,job_json_data)
        return {"message" : 'acquired'}
    return None
