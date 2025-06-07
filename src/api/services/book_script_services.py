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
#exceptions
from fastapi.exceptions import HTTPException
# checks itself vs api service keys , leave script to handle the values
SERVICE_MAP = {
    "find" : "getbook",
    "find_hardmode" : "getbook-adv",
    "pick" : "pick"

}
VALID_SERVICE = set(SERVICE_MAP.values())

async def book_service_dispatch(*,service: str, search_query: UnknownBook, user: UserDetails) -> tuple[bool,str]:
    """
    Trying out service map due to leaning out of other services to purely option changes.
    """
    """
    Service dispatcher for book related api services.

    After refactoring lots of code re-used only option changes.Map out option and let it be passed in via routes layer.

    Args:
        service (str): i.e. the option to run selenium script with
        search_query (UnknownBook): Pydantic model used for request validation and data parsing
        user (UserDetails): ^
    """
    if service not in VALID_SERVICE:
        raise HTTPException(status_code=400,detail=f"Bad request service option: '{service}'")
    
    script_options = build_script_options(search_query=search_query, user=user, option=SERVICE_MAP[service])
    
    #already built our kwarg params , just unpack via **
    script_results: tuple[bool,str] = await coroutine_runner(
        book_bot,
        **script_options
    )
    return script_results

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
    
    script_result= await coroutine_runner(book_bot,**script_options)
    #moved post processing to route layer wrapper
    return script_result
    

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