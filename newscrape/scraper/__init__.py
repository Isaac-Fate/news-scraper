import requests
from datetime import date, timedelta
from itertools import filterfalse
from concurrent.futures import ThreadPoolExecutor, wait
from bs4 import BeautifulSoup
from ..db import NewsDBClient
from ..schema import Language
from ..schema.news import LINK
from .search import (
    HEADERS,
    search_news
)
from ..webdriver import WebDriver
from .headline import (
    find_news_headline_from_news_post_html,
    NewsHeadlinePicker
)

class NewsScraper:
    
    def __init__(
            self, 
            db_client: NewsDBClient,
            web_driver: WebDriver,
            headline_picker: NewsHeadlinePicker,
            n_workers: int = 1
        ) -> None:
        
        self._db_client = db_client
        self._web_driver = web_driver
        self._headline_picker = headline_picker
        self._executor = ThreadPoolExecutor(max_workers=n_workers)
    
    @property
    def db_client(self) -> NewsDBClient:
        return self._db_client
    
    @property
    def web_driver(self) -> WebDriver:
        return self._web_driver
    
    @property
    def headline_picker(self) -> NewsHeadlinePicker:
        return self._headline_picker
        
    def scrape_news(
            self,
            query: str,
            date_start: date = date.today(),
            date_end: date = date.today(),
            language: Language | str = Language.English
        ):
        """Scrapte news information and then store into MongoDB.

        Parameters
        ----------
        query : str
            Search query
        date_start : date, optional
            Starting date, by default date.today()
        date_end : date, optional
            End date, by default date.today()
        language : Language | str, optional
            Only show the result in the pecified language, by default Language.English
        """
        
        """
        Phase 1
        -------
            Scrape news directly from search results.
        """
        
        self.search_and_store_news(
            query=query,
            date_start=date_start,
            date_end=date_end,
            language=language
        )
        
        """
        Phase 2
        -------
            Visit the news post website and find more information.
        """
        
        news_with_truncated_headlines = self._db_client.find_news_with_truncated_headlines()
        
        for news in news_with_truncated_headlines:
            
            news_link = news.get(LINK, None)
            if news_link is None: continue
            
            # we want to get the HTML content of the news post website
            
            # get HTML via a simple GET request
            res = requests.get(
                url=news_link,
                headers=HEADERS
            )
            if res.ok:
                news_post_html = res.content
                
            # get HTML using a web driver
            else:
                news_post_html = self._web_driver.get_html(url=news_link)
            
            # find the suitable news headline
            news_headline = find_news_headline_from_news_post_html(
                html=news_post_html,
                picker=self._headline_picker
            )
            
            # update the headline
            self._db_client.update_news_headline(
                id=news.id,
                headline=news_headline
            )

    def search_and_store_news(
            self,
            query: str,
            date_start: date = date.today(),
            date_end: date = date.today(),
            language: Language | str = Language.English
        ):
        """Use Google to search for news and then store them in MongoDB.
        
        Notes
        -----
            The requests will be sent concurrently via multiple threads.
            
            Note that all the news information is retrieve
            directly from the search results.
            We will NOT look into the website of the news post.
            Therefore, some headlines may be truncated!

        Parameters
        ----------
        query : str
            Search query
        date_start : date, optional
            Starting date, by default date.today()
        date_end : date, optional
            End date, by default date.today()
        language : Language | str, optional
            Only show the result in the pecified language, by default Language.English
        """
        
        # number of days to search
        n_days = (date_end - date_start).days
        
        # starting date
        date = date_start
        
        # list of Future instances
        futures = []
        
        # assign tasks to multiple threads
        for _ in range(n_days):
            
            date += timedelta(days=1)
            
            # submit a task to the executor
            future = self._executor.submit(
                self.search_and_store_news_on_date,
                query=query,
                date=date,
                language=language
            )
            
            futures.append(future)
        
        # wait for all tasks to complete
        wait(futures)
        
    def search_and_store_news_on_date(
            self,
            query: str,
            date: date = date.today(),
            language: Language | str = Language.English
        ):
        
        # scrape a list of news from Google Search
        news_list = search_news(
            query=query,
            date=date,
            language=language
        )
        
        # filter out those news whose links
        # already exist in the database
        news_list = list(filterfalse(
            lambda news: self._db_client.does_news_link_exist(news[LINK]),
            news_list
        ))
        
        # insert into database
        self._db_client.insert_many_news(news_list)
        
__all__ = [
    'NewsScraper'
]
