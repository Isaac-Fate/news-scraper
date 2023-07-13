from typing import Optional
from datetime import date, datetime
import requests
import urllib.parse
from bs4 import BeautifulSoup, Tag
from ..schema import News, Language
from ..schema.news import (
    DATE, 
    PUBLICATION,
    HEADLINE,
    LINK
)
from ..db import IS_HEADLINE_TRUNCATED
from .utils import (
    GOOGLE,
    HEADERS,
    DATE_FORMAT
)

def search_news(
        query: str,
        date: date = date.today(),
        language: Language | str = Language.English
    ) -> list[News]:
    
    # create the search URL
    url = create_search_url(query, date, language)
    
    # send the request
    res = requests.get(
        url=url,
        headers=HEADERS
    )
    assert res.ok, \
        f'Failed to send request to {url}'
    
    # make soup
    soup = BeautifulSoup(res.content, features='lxml')
    
    # search results
    search_result_tags = soup.find_all(
        name='div',
        attrs={
            'class': 'SoaBEf'
        }
    )
    
    # a list of news
    news_list: list[News] = []
    for tag in search_result_tags:
        
        publication = find_news_publication(tag)
        headline = find_news_headline_from_search_result_tag(tag)
        link = find_news_link(tag)
        
        # create a news instance
        news = News({
            DATE: date.strftime(DATE_FORMAT),
            PUBLICATION: publication,
            HEADLINE: headline,
            LINK: link
        })
        
        # set the is_headline_truncated flag
        if is_news_headline_truncated(headline):
            news[IS_HEADLINE_TRUNCATED] = True
        
        # collect the news
        news_list.append(news)
    
    return news_list

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

def find_news_headline_from_search_result_tag(tag: Tag) -> Optional[str]:
    
    # the tag containing the headline
    headline_tag = tag.find(
        name='div',
        attrs={
            'role': 'heading'
        }
    )
    if headline_tag is None: return None
    
    # extract the headline
    headline = headline_tag.text
    
    # remove newline characters
    headline = headline.strip().replace('\n', '')
    
    return headline

def is_news_headline_truncated(headline: str) -> bool:
    
    return headline.endswith('...')
