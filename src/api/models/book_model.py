from pydantic import BaseModel

class UnknownBook(BaseModel):
    title: str
    author: str | None = ""

class UserDetails(BaseModel):
    username: str