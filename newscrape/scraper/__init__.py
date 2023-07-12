import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
from ..db import NewsDBClient, IS_HEADLINE_TRUNCATED
from ..news import (
    News,
    DATE,
    PUBLICATION,
    HEADLINE,
    LINK
)
from ..webdriver import WebDriver
from ..headline import (
    find_news_headline_from_search_result_tag,
    is_news_headline_truncated,
    find_news_headline_from_news_post_html,
    NewsHeadlinePicker
)
from ..language import Language
from .utils import (
    HEADERS, 
    DATE_FORMAT,
    create_search_url,
    find_news_publication,
    find_news_link
)

__all__ = [
    'NewsScraper'
]

class NewsScraper:
    
    def __init__(
            self, 
            db_client: NewsDBClient,
            web_driver: WebDriver,
            headline_picker: NewsHeadlinePicker
        ) -> None:
        
        self._db_client = db_client
        self._web_driver = web_driver
        self._headline_picker = headline_picker
        
    def scrape_news(
            self,
            query: str,
            date_start: date = date.today(),
            date_end: date = date.today(),
            language: Language | str = Language.English
        ):
        
        #########
        # PHASE 1
        #########
        
        n_days = (date_end - date_start).days
        date = date_start
        
        for _ in range(n_days):
            
            date += timedelta(days=1)
        
            self._roughly_scrape_news_on_date(
                query=query,
                date=date,
                language=language
            )
        
        #########
        # PHASE 2
        #########
        
        news_with_truncated_headlines = self._db_client.find_news_with_truncated_headlines()
        
        for news in news_with_truncated_headlines:
            
            news_link = news.get(LINK, None)
            if news_link is None: continue
            
            res = requests.get(
                url=news_link,
                headers=HEADERS
            )
            
            if res.ok:
                news_post_html = res.content
                
            else:
                news_post_html = self._web_driver.get_html(url=news_link)
                
            news_headline = find_news_headline_from_news_post_html(
                html=news_post_html,
                picker=self._headline_picker
            )
            
            self._db_client.update_news_headline(
                id=news.id,
                headline=news_headline
            )

    def _roughly_scrape_news_on_date(
            self,
            query: str,
            date: date = date.today(),
            language: Language | str = Language.English
        ):
        
        # create the search URL
        url = create_search_url(query, date, language)
        
        # send the request
        res = requests.get(
            url=url,
            headers=HEADERS
        )
        assert res.ok
        
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
            
            # do nothing if the link already exists
            if self._db_client.does_news_link_exist(link):
                continue
            
            # create a news instance
            news = News({
                DATE:date.strftime(DATE_FORMAT),
                PUBLICATION: publication,
                HEADLINE: headline,
                LINK: link
            })
            
            # set the is_headline_truncated flag
            if is_news_headline_truncated(headline):
                news[IS_HEADLINE_TRUNCATED] = True
            
            # collect the news
            news_list.append(news)
            
        # insert into database
        self._db_client.insert_many_news(news_list)
        