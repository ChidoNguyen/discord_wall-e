from fastapi import APIRouter , BackgroundTasks
from typing import Callable , Awaitable
#models
from src.api.models.book_model import UnknownBook, UserDetails
#services
from src.api.services.book_script_services import find_service, find_hardmode_service, pick_service, catalog_service , overtime_jobs
book_script = APIRouter()

@book_script.get("/")
async def home():
    print("HomePagePlaceHolder")
    return {"message" : "homepage"}

# just a note to self ... Callable type hinting Args,Returns
#
async def book_script_route_service_handler(
        service_function: Callable[...,Awaitable],
        background_tasks: BackgroundTasks,
        *args, **kwargs
):
    """
    Wrapper to incorporate both service function execution and a clean up coupled with it via background_tasks. Since repeated code among the services with slight changes, wrapper to help with code re-use made sense.

    Args :
        service_function (Callable): Name of the service function
        background_tasks (BackgroundTasks): handles our background tasks running

    """
    # service function signatures are all the same
    response = await service_function(*args,**kwargs)
    if response.get('success'):
        background_tasks.add_task(overtime_jobs)
    return response

@book_script.post("/whisperfind")
@book_script.post("/find")
async def find(search_query: UnknownBook, user: UserDetails , background_tasks: BackgroundTasks):
    return await book_script_route_service_handler(find_service,background_tasks,search_query=search_query,user=user)



@book_script.post("/find_hardmode")
async def find_hardmode(search_query: UnknownBook, user: UserDetails):
    return await find_hardmode_service(search_query=search_query,user=user)

@book_script.post("/pick")
async def pick(search_query: UnknownBook, user: UserDetails):
    return await pick_service(search_query=search_query,user=user)

@book_script.get("/catalog")
async def catalog():
    return await catalog_service()

@book_script.post("/donezo")
async def done():
    return None