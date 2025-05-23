from ebooklib import epub
import warnings
import re
####ebooklib future/user warning ######
warnings.filterwarnings(
    'ignore', 
    message = 'In the future version we will turn default option ignore_ncx to True.', 
    category=UserWarning
    )
warnings.filterwarnings(
    'ignore',
    message=(".*This search incorrectly ignores the root element, and will be fixed in a future version.*"),
    category=FutureWarning
    )
###########                 ###########

def _sanitize_str(data_string : str) -> str:
    return re.sub(r'[<>:"/\\|?*]','', data_string)

def _load_file(*,file_path: str) -> epub.EpubBook:
    ''' loads epub'''
    return epub.read_epub(file_path)

def _get_data_DC(*,epub_doc : epub.EpubBook) -> dict[str,str]:
    _epub_space = 'DC'
    author = _sanitize_str(epub_doc.get_metadata(_epub_space,'creator')[0][0])
    title = _sanitize_str(epub_doc.get_metadata(_epub_space,'title')[0][0])

    #white space clearing
    return {'author' : author , 'title': title}

def _build_data_dict(*, data: dict[str,str]) -> dict[str,str]:
    """generates our required data dict structure 
    
    args : dict[str,str]  keys : [`title`,`author`]

    returns dict[str,str] with keys [`title`,`fname`,`lname`]

    """
    #clean up white spaces in author
    author = data['author']
    author = ' '.join(author.strip().split())
    fname , lname = "" , ""
    if ',' in author: 
        name_parse = [n.strip() for n in author.split(',',1)]
        lname = name_parse[0]
        if len(name_parse) > 1:
            fname = name_parse[1]
    else:
        name_parse = author.split()
        if len(name_parse) == 1:
            lname = name_parse[0]
        else:
            lname = name_parse[-1]
            fname = ' '.join(name_parse[:-1]) 

    return {'fname' : fname, 'lname': lname, 'title': data['title']}

def get_meta_data(*, file_path: str):
    """
    Extracts epub metadata

    Arguments : Takes full file path

    Returns : dictionary with metadata , key values [`lname`,`fname`,`title`]

    """
    literature = _load_file(file_path=file_path)
    data = _get_data_DC(epub_doc=literature)
    return _build_data_dict(data=data)
    