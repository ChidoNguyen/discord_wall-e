import aiohttp
import json
from dataclasses import asdict
from urllib.parse import urljoin
from typing import Any
from src.discord_bot.models.book_models import BookCogPayload,UserDetails,SearchQuery
#errors

class BookApiClient:
    """ Manages API related operations and information for BOOK cog."""
    def __init__(self,*,base_url: str, api_session: aiohttp.ClientSession | None = None):
        self.base_url = base_url

        #helps regulate if session was given or self created for management
        if api_session is None:
            self.api_client = aiohttp.ClientSession()
            self._self_session = True
        else:
            self.api_client = api_session
            self._self_session = False

        self.api_routes = {
            'find' : '/find',
            'find_hardmode' : '/find_hardmode',
            'pick' : '/pick',
            'catalog' : '/catalog',
            'dm' : '/whisperfind'
        }

    async def close(self):
        if self._self_session:
            await self.api_client.close()

    def _build_request_payload(self, *, username: str, title: str, author: str) -> dict[str,Any]:

        """
        Builds BOOK api specific request payload to pass validation and verification models.
        """
        payload = BookCogPayload(
            search_query=SearchQuery(title=title,author=author),
            user_details=UserDetails(username=username)
        )
        return asdict(payload)
    
    def _get_api_endpoint(self, option: str) -> str:
        """ Returns the full url with api endpoint; specific to option value."""
        try:
            return urljoin(self.base_url, self.api_routes[option.lower().strip()])
        except KeyError:
            raise ValueError(f"Invalid API route option [`{option.lower().strip()}`] ")
    
    async def _post(self,*, url: str, payload: dict[str,Any]):
        """ Post request to the api. """
        try:
            async with self.api_client.post(url,json=payload) as response:
                if response.status == 200:
                    return json.loads(await response.json())
                else:
                    print(f"Non 200 response from API: {response.status} for [url : {url}]")
        except aiohttp.ClientError as e:
            print(f"HTTP client error occured: [Cog: Book] [Error: {e}]")
        except Exception as e:
            print(f"Unexpected POST operation exception/error: [Cog: Book] [Error: {e}]")
        return None
    
    async def post_to_api(self,*,title: str, author: str, username: str, option: str) -> dict[str,Any] | None:

        """ POST request to API 
        
        Function does all the heavy lifting. Builds payload, generates full URL, and checks for a 200 response.

        
        
        """
        url = self._get_api_endpoint(option)
        payload = self._build_request_payload(username= username, title= title, author= author)
        #return await self._post(url=url,payload=payload)
        response = await self._post(url=url, payload=payload)
        return response
