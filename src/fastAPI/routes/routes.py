from fastapi import APIRouter , BackgroundTasks
from pydantic import BaseModel
from typing import Dict , Any , Union
from ..services import find_service , find_hardmode_service, pick_service , cron_fake , catalog_service

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

@router.post("/find")
async def find(unknown_book : UnknownBook, user_details : UserDetails, background_tasks : BackgroundTasks):
    #print("looking")
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_service(book_info,user_info)
    #print(novel)
    '''
    Novel should be full JSON output could probably parse out meta data in "services" but for now skeleton it here
    '''
    ###
    # _ , _ values are steps and misc for debugging if needed
    #req_status , job_json_data , message , _ , _ = novel.values()
    req_message , req_data = novel.values()
    #can narrow down check on novel for extra check but services already check that status is success
    ###
    if novel is not None:
        background_tasks.add_task(cron_fake,req_data)
        return {"message" : 'acquired'}
    return None

@router.post("/find_hardmode")
async def find_hardmode(unknown_book : UnknownBook, user_details : UserDetails):
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await find_hardmode_service(book_info,user_info)
    if novel is not None:
        return {"message" : 'found some stuff'}
    return None

@router.post("/pick")
async def pick(unknown_book : UnknownBook, user_details: UserDetails,background_tasks: BackgroundTasks):
    book_info = unknown_book.model_dump()
    user_info = user_details.model_dump()
    novel = await pick_service(book_info,user_info)
    message, job_json_data = novel.values()
    if novel is not None:
        background_tasks.add_task(cron_fake,job_json_data)
        return {"message" : 'acquired'}
    return None

@router.get("/catalog")
async def catalog():
    magazine = await catalog_service()
    if magazine is not None:
        return
    return None