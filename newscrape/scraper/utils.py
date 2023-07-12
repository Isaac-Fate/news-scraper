from typing import Optional
from datetime import date, datetime
import urllib.parse
from bs4 import Tag
from ..language import Language

GOOGLE = 'https://www.google.com'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0'
HEADERS = {
    'User-Agent': USER_AGENT
}
DATE_FORMAT = '%Y-%m-%d'

def create_search_url(
        query: str,
        date: date = date.today(),
        language: Language | str = Language.English
    ) -> str:
    
    # base URL
    url = GOOGLE
    
    # get language
    if not isinstance(language, Language):
        if isinstance(language, str):
            language = Language.from_str(language)
        else:
            raise ValueError('invalid input of language')
    
    # search content
    url += f"/search?q={urllib.parse.quote(query)}"
    
    # search for news
    url += f"&tbm=nws"
    
    # get correct date format and then search by date
    date_query_str = datetime.strftime(date, "%m/%d/%Y")
    url += f"&tbs=cdr:1,cd_min:{date_query_str},cd_max:{date_query_str}"
    
    # sort by relevancy
    url += f",sbd:0"
    
    # we want results in english
    url += f"&lr={language.to_url_query_value()}"
    
    return url
    
def find_news_publication(tag: Tag) -> Optional[str]:
    
    # publication icon image
    publication_img_tag = tag.find(name='g-img')
    if publication_img_tag is None: return None
    
    # the parent tag containing the publication name
    publication_tag = publication_img_tag.parent
    
    # extract publication name
    publication_span_tag = publication_tag.find(name='span')
    if publication_span_tag is None: return None
    publication = publication_span_tag.text
    
    return publication

def find_news_link(tag: Tag) -> Optional[str]:
        
    link_tag = tag.find(name='a')
    if link_tag is None: return None
    link = link_tag.get('href', None)

    return link