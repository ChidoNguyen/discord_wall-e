import asyncio
#models
from src.api.models.book_model import UnknownBook, UserDetails
#utils
from src.api.utils.book_route_util import build_script_options , format_script_result , check_overtime, create_database_job
from src.api.utils.db_util import insert_database
from src.api.utils.cache_data import fetch_catalog_cache

from src.api.utils.thread_helper import coroutine_runner
#script
from src.selenium_script.main import book_bot
#exception
from src.api.utils.book_route_util import ScriptServiceExceptionError

async def service_script_handler(*,search_query: UnknownBook, user: UserDetails, option: str) -> dict:
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

    # tuple treated as status,msg (bool,json output)
    script_result= await coroutine_runner(book_bot,**script_options)
    try:
        response_msg = format_script_result(script_result)
        if option in {'getbook','pick'}:
            #script response_msg[]
            metadata = response_msg['payload']
            create_database_job(metadata)
        return response_msg
    except ScriptServiceExceptionError as e:
        print(e)
    return {}

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

async def find_hardmode_service(*, search_query: UnknownBook, user: UserDetails,option:str = 'getbook-adv') -> dict:
    """
    Run the advanced book search service.

    Args and Returns: same as `find_service`.
    """
    return await service_script_handler(search_query=search_query, user=user, option=option)

async def pick_service(*, search_query: UnknownBook, user: UserDetails,option:str = 'pick') -> dict:
    """
    Run the pick service for selecting books.

    Args and Returns: same as `find_service`.
    """
    return await service_script_handler(search_query=search_query, user=user, option=option)

async def overtime_jobs():
    """
    Checks our overtime folder aka any outstanding tasks that should be executed to give most up to date content. tasks is file i/o behaviours.
    """
    try:
        extra_pay_listings = await asyncio.to_thread(check_overtime)
        if extra_pay_listings:
            await asyncio.to_thread(insert_database,all_jobs=extra_pay_listings)
    except Exception as e:
        print(f"bad jobs {e}")
    return

async def catalog_service() -> dict:
    """ Snapshot of what we have on hand. """
    await overtime_jobs()
    catalog_data = await fetch_catalog_cache(json_transfer=True)
    return {'catalog' : catalog_data}