import json
from dataclasses import dataclass

from src.api.models.book_model import UnknownBook , UserDetails

@dataclass
class ScriptServiceExceptionError(Exception):
    message : str
    module: str 
    action : str | None = None
    def __str__(self):
        return (
            f"[{self.module}] {self.message} |"
            f"{f'[Action] {self.action} |' if self.action else ''}"
        )

def build_script_options(*,search_query: UnknownBook , user: UserDetails, option:str ) -> dict[str,str]:
    """
    Builds selenium script required arguments.

    Args:
        search_query (UnknownBook) : title / author members
        user (UserDetails) : username member
        option (str) : option we are running
    Returns:
        dict[str,str]: keys are script required args `search`, `user`, `option`.
    """
    search_info = search_query.model_dump()
    user_info = user.model_dump()

    author = search_info['author']
    title = search_info['title']

    search_term = f"{title} {author}".strip()

    return {
        "search" : search_term,
        "user" : user_info['username'],
        "option" : option
    }

def parse_script_result(result) -> dict:
    # need to refine script out 
    #assume dict for now ..
    try:
        result_info = json.loads(result)
        if result_info.get('status') == 'success':
            return {
                'message' : result_info.get('message'),
                'metadata' : result_info.get('metadata')
            }
        return {}
    except Exception as e:
        raise ScriptServiceExceptionError(
            module="API_Book_Utils",
            message="Could not parse script result.",
            action="json.loads()",
        )
