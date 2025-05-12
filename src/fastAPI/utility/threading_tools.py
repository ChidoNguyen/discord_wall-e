import asyncio

#   lambda : asyncio.run(some_async_function_that()) 
#   ^ masks an async function as non async , no bueno 
'''
might need for pi4 later


from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)
'''

def coroutine_in_thread(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(coroutine)
        return results
    finally:
        loop.close()

async def coroutine_runner(coroutine,*args,**kwargs):
    def func_wrapper():
        return coroutine_in_thread(coroutine(*args,**kwargs))
    return await asyncio.to_thread(func_wrapper)