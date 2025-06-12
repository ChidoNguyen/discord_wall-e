from fastapi import APIRouter, BackgroundTasks
#models
from src.api.models.book_model import UnknownBook, UserDetails
#services
from src.api.services.book_script_services import book_service_dispatch, catalog_service , overtime_jobs
#utils
from src.api.utils.book_route_util import format_script_response, format_script_result, create_database_job

book_script = APIRouter()

@book_script.get("/")
async def home():
    print("HomePagePlaceHolder")
    return {"message" : "homepage"}

async def book_script_route_handler(*, service: str, search_query: UnknownBook, user: UserDetails, background_tasks: BackgroundTasks):
    background_task_map = {
        "find" : overtime_jobs,
        "pick" : overtime_jobs
    }
    #run our service dispatcher 
    raw_service_response = await book_service_dispatch(
        service=service,
        search_query=search_query,
        user=user
    )
    response = format_script_result(raw_service_response)
    
    #if service was good and needs post processing
    if response.get('success', False) and service in {'find', 'pick'}:
        #create a db job + attempt clean up
        create_database_job(response['payload'])
        background_tasks.add_task(background_task_map[service])

    return format_script_response(response)

@book_script.post("/whisperfind")
@book_script.post("/find")
async def find(unknown_book: UnknownBook, user: UserDetails , background_tasks: BackgroundTasks):
    return await book_script_route_handler(
        service='find',
        search_query=unknown_book, 
        user=user, 
        background_tasks=background_tasks
        )



@book_script.post("/find_hardmode")
async def find_hardmode(unknown_book: UnknownBook, user: UserDetails, background_tasks: BackgroundTasks):
    return await book_script_route_handler(
        service='find_hardmode',
        search_query=unknown_book, 
        user=user, 
        background_tasks=background_tasks
        )

@book_script.post("/pick")
async def pick(unknown_book: UnknownBook, user: UserDetails, background_tasks: BackgroundTasks):
    return await book_script_route_handler(
        service='pick',
        search_query=unknown_book, 
        user=user, 
        background_tasks=background_tasks
        )

@book_script.get("/catalog")
async def catalog():
    return await catalog_service()

@book_script.post("/donezo")
async def done():
    return None



"""
# just a note to self ... Callable type hinting Args,Returns
# moved to script dispatcher with option arg as strings and mapping
async def book_script_route_service_handler(
        service_function: Callable[...,Awaitable[dict[str,Any]]],
        background_tasks: BackgroundTasks,
        *args, **kwargs
):
    
    Wrapper to incorporate both service function execution and a clean up coupled with it via background_tasks. Since repeated code among the services with slight changes, wrapper to help with code re-use made sense.

    Args :
        service_function (Callable): Name of the service function
        background_tasks (BackgroundTasks): handles our background tasks running

    
    #services that need BG_TASK map
    # function to function relation can swap out who/what if needed.
    background_task_map: dict[Callable,Callable] = {
        find_service : overtime_jobs,
        pick_service : overtime_jobs
    }
    # service function signatures are all the same
    response = await service_function(*args,**kwargs)
    if response.get('success', False) and service_function in background_task_map:
        background_tasks.add_task(background_task_map[service_function])
    return response
"""