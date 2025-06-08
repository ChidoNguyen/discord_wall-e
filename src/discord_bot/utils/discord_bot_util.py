import os

def _fetch_cogs(*,cogs_path: str) -> list[str]:
    """ gets us file names in cogs directory """
    return [ entry.name[:-3] for entry in os.scandir(cogs_path) if entry.is_file() and "__init__" not in entry.name ]
    

def _base_cog_path(*,cogs_path: str):
    """ builds the dot notation of our cogs directory to use as a base name. """
    #starter is `src`
    s_index = cogs_path.find('src')
    if s_index >= 0:
        bot_cogs_base = cogs_path[s_index:]
        #split and join or swap out /
        dot_base = ('.').join(bot_cogs_base.split('/'))
        return dot_base
    return ""

def _build_cog_dot_path(*,base: str, cogs: list[str]) -> list[str]:
    """ builds the full cogs name with dot base path. """
    return [f"{base}.{cog}" for cog in cogs]

def get_bot_cogs(*,cogs_path: str) -> list[str]:
    cogs = _fetch_cogs(cogs_path=cogs_path)
    base_dot_path = _base_cog_path(cogs_path=cogs_path)
    if cogs and base_dot_path:
        return _build_cog_dot_path(base=base_dot_path,cogs=cogs)
    return []

if __name__ == '__main__':
    pass