import aiohttp
from urllib.parse import urljoin
#errors

class BookApiClient:
    def __init__(self,*,base_url: str, api_session: aiohttp.ClientSession | None):
        self.base_url = base_url
        if api_session is None:
            self.api_client = aiohttp.ClientSession()
            self._self_session = True
        else:
            self.api_client = api_session
            self._self_session = False

    async def close(self):
        if self._self_session:
            await self.api_client.close()

    async def post_to_api(self,*,end_point:str, payload: dict):
        #things request payload needs
        # 1) username
        url = urljoin(self.base_url,end_point)
        try:
            async with self.api_client.post(url,json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Non 200 response from API: {response.status} for {end_point}")
        except aiohttp.ClientError as e:
            print(f"HTTP client error occured: [Cog: Book] [Error: {e}]")
        except Exception as e:
            print(f"Unexpected POST Error in Book Cog: {e}")
        return None