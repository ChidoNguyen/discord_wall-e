from dataclasses import dataclass

@dataclass
class SearchQuery:
    title: str
    author: str = ""
    

@dataclass
class UserDetails:
    username: str

@dataclass
class BookCogPayload:
    search_query: SearchQuery
    user_details: UserDetails