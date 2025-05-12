import asyncio
from datetime import datetime
##### Scaffold to see/ensure async spin ups ######
from src.fastAPI.services import find_service , find_hardmode_service
 
async def test_wrapper(name : str , data, func ):
    start_time = f"[{datetime.now()}]"
    results = await func(**data)
    end_time = f"[{datetime.now()}]"
    return {'func' : name , 'start_time' : start_time, 'end_time' : end_time}


def give_me_data(opt: str):
    user = {'username' :'test_concurrency'}
    search = {'find' : {'title' : 'local missing woman' , 'author' : 'mary kubica'} , 'find_hard' : {'title' : 'art of war' , 'author' : ''}, 'pick' : ''}
    return { 'book_info' : search[opt] , 'user_info' : user}
    #return { "user" : user , "search" : search[opt],"option" : commands[opt]}

async def main():
    print(f"[{datetime.now()}] Starting test for api concurrency.")
    results = await asyncio.gather(
        test_wrapper('find',give_me_data('find'),find_service),
        test_wrapper('find_hard', give_me_data('find_hard'),find_hardmode_service)
    )

    print(f"[{datetime.now()}] All done. Results: ")
    for r in results :
        print("→", r)
if __name__ == "__main__":
    asyncio.run(main())
