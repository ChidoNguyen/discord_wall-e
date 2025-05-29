import json

#models
from src.api.models.book_model import UnknownBook, UserDetails
#utils
from src.api.utils.book_route_util import build_script_options , parse_script_result
from src.api.utils.thread_helper import coroutine_runner
#script
from src.selenium_script.main import book_bot
#exception
from src.api.utils.book_route_util import ScriptServiceExceptionError

async def find_service(*,search_query: UnknownBook, user:UserDetails,option: str = "getbook"):
    script_options = build_script_options(search_query=search_query, user=user, option=option)

    #helps not block api#
    script_result = await coroutine_runner(book_bot,user=script_options['user'], search=script_options['search'],option=option)

    try:
        return parse_script_result(script_result)
    except ScriptServiceExceptionError as e:
        #log here maybe , pre placed just incase
        print(e)
    return None
    
async def find_hardmode_service(*,search_query: UnknownBook, user: UserDetails, option: str = "getbook-adv"):
    script_options = build_script_options(search_query=search_query, user=user, option=option)
    script_result = await coroutine_runner(book_bot,user=script_options['user'], search=script_options['search'],option=option)
    try:
        return parse_script_result(script_result)
    except ScriptServiceExceptionError as e:
        print(e)
    return None

async def pick_service(*,search_query: UnknownBook, user: UserDetails, option: str = "pick"):
    script_options = build_script_options(search_query=search_query, user=user, option=option)
    script_result = await coroutine_runner(book_bot,user=script_options['user'], search=script_options['search'],option=option)
    try:
        return parse_script_result(script_result)
    except ScriptServiceExceptionError as e:
        print(e)
    return None

async def catalog_service():
    return None