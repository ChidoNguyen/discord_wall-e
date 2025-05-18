import argparse

BOT_SETTINGS = {'getbook', 'getbook-adv', 'pick'}

def parse_arg(argv: list[str] | None = None) -> tuple[str, str, str]:
    """
    Function : Parses our command line argument
    
    Arguments : COMMAND LINE ARGUMENTS
        --search : str : full search query
        --user : str : username
        --option : str : getbook / getbook-adv / pick

    Returns : 
        tuple containing (user,search,option)
    """
    parser = argparse.ArgumentParser(description="book_bot_kwargs")
    
    parser.add_argument('--search' , type=str, required=True,
                        help= 'Search string used to designate what to look for.')
    parser.add_argument('--user' , type = str , required= True,
                        help = "User's name to help with file organization and task tracking.")
    parser.add_argument('--option', type = str, required= True,
                        choices=['getbook','getbook-adv','pick'], help= 'Designates the bot for usage type among: getbook ,getbook-adv, pick')

    args = parser.parse_args(argv)
    return args.user, args.search, args.option

def direct_script_arg_validation(user: str, search: str, option: str) -> tuple[bool,str]:
    """ Verifies function calls has necessary arguments """
    if option not in BOT_SETTINGS:
        return False, 'Invalid option choice.'
    elif not user.strip():
        return False, 'Missing user value.'
    elif not search.strip():
        return False, 'Missing search value.'
    else:
        return True, ''
