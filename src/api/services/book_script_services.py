#models
from src.api.models.book_model import UnknownBook, UserDetails
#utils
from src.api.utils.book_route_util import build_script_options , format_script_result , overtime_jobs, add_to_catalog , clean_job_listing

from src.api.utils.thread_helper import coroutine_runner
#script
from src.selenium_script.main import book_bot
#exception
from src.api.utils.book_route_util import ScriptServiceExceptionError

async def service_script_handler(*,search_query: UnknownBook, user: UserDetails, option: str):
    """
    Service wrapper for book related api services.

    Logic code is the same, changes based on options. Script wrapper will build dict of required kwargs option changes as needed. But this allows all service route to call same code block.

    Args:
        search_query (UnknownBook): Pydantic model used for request validation and data parsing
        user (UserDetails): ^
        option (str): Used to leverage different script tasks 
    """
    script_options= build_script_options(search_query=search_query,user=user,option=option)
    '''
    book_bot selenium script returns json formatted script status that was tracked during script execution. 'status' will have success if done properly
    '''
    script_result= await coroutine_runner(book_bot,**script_options)
    try:
        return format_script_result(script_result)
    except ScriptServiceExceptionError as e:
        print(e)
    return

async def find_service(*, search_query: UnknownBook, user: UserDetails,option:str = 'getbook'):
    """
    Run the standard book search service.

    Args:
        search_query (UnknownBook): Validated search query data.
        user (UserDetails): User details for request context.
        option (str, optional): Script option flag. Defaults to 'getbook'.

    Returns:
        Parsed result from the script handler or None on failure.
    """
    return await service_script_handler(search_query=search_query, user=user, option=option)

async def find_hardmode_service(*, search_query: UnknownBook, user: UserDetails,option:str = 'getbook-adv'):
    """
    Run the advanced book search service.

    Args and Returns: same as `find_service`.
    """
    return await service_script_handler(search_query=search_query, user=user, option=option)

async def pick_service(*, search_query: UnknownBook, user: UserDetails,option:str = 'pick'):
    """
    Run the pick service for selecting books.

    Args and Returns: same as `find_service`.
    """
    return await service_script_handler(search_query=search_query, user=user, option=option)

async def catalog_service():
    #get any jobs to be update
    #send it to the work pool
    job_pool = await overtime_jobs()
    for task in job_pool:
        new_file = await add_to_catalog(task)
        if new_file:
            clean_job_listing(job_file=task,new_file_path=new_file)
    
    return {'catalog' : get_cache_data()}