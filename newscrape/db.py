from typing import Self, Optional, Iterable
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from .schema import News
from .schema.news import (
    HEADLINE,
    LINK
)

NEWS_COLLECTION_NAME = 'news'
IS_HEADLINE_TRUNCATED = 'is_headline_truncated'

class NewsDBClient(MongoClient):
    
    def __init__(self, *, database_name: str, **kwargs):
        
        super().__init__(**kwargs)
        
        # get the database
        self._datebase = self.get_database(database_name)
        
        # news collection
        self._news_collection = self._datebase.get_collection(NEWS_COLLECTION_NAME)
    
    @classmethod
    def from_host_and_port(
            cls, *, 
            database_name: str, 
            host: str, 
            port: int
        ) -> Self:
        
        return cls(
            database_name=database_name,
            host=host,
            port=port
        )
    
    def insert_one_news(self, news: News) -> Optional[ObjectId]:
        
        # insert into database
        insertion_result = self._news_collection.insert_one(news)
        
        # inserted ID
        return insertion_result.inserted_id
    
    def insert_many_news(self, news_collection: Iterable[News]) -> list[ObjectId]:
        
        # do nothing if there are no news
        if len(news_collection) == 0: return []
        
        # insert into database
        insertion_result = self._news_collection.insert_many(news_collection)
        
        # inserted IDs
        return insertion_result.inserted_ids
    
    def does_news_link_exist(self, link: str) -> bool:
        
        return self._news_collection.find_one(
            filter={
                LINK: {
                    '$eq': link
                }
            }
        ) is not None
    
    def find_all_news(self, fields: list[str] = []) -> list[News]:
        
        return list(map(
            News.from_document,
            self._news_collection.find(
                filter={},
                projection=fields
            )
        ))
        
    def find_news_with_truncated_headlines(self) -> list[News]:
        
        return list(map(
            News.from_document,
            self._news_collection.find(
                filter={
                    IS_HEADLINE_TRUNCATED: True
                }
            )
        ))
        
    def find_news_inserted_within_date_time_range(
            self,
            date_time_start: datetime.now(),
            date_time_end: datetime.now(),
            fields: list[str] = []
        ):
        
        return list(map(
            News.from_document,
            self._news_collection.find(
                filter={
                    '$expr': {
                        '$and': [
                            {'$gte': [{'$toDate': '$_id'}, date_time_start]},
                            {'$lte': [{'$toDate': '$_id'}, date_time_end]}
                        ]
                    }
                },
                projection=fields
            )
        ))
    
    def find_news_inserted_in_past_n_hours(
            self,
            hours: int = 1,
            fields: list[str] = []
        ):
        
        # current data time
        now = datetime.now()
        
        return self.find_news_inserted_within_date_time_range(
            date_time_start=now - timedelta(hours=hours),
            date_time_end=now,
            fields=fields
        )
    
    def find_all_news_links(self) -> list[str]:
        
        links = []
        document: dict
        for document in self._news_collection.find(filter={}, projection={'_id': 0, LINK: 1}):
            link = document.get(LINK, None)
            if link is not None:
                links.append(link)
        
        return links
    
    def update_news_headline(self, id: ObjectId, headline: str):
        
        self._news_collection.update_one(
            filter={
                '_id': id
            },
            update={
                '$set': {
                    HEADLINE: headline
                },
                '$unset': {
                    IS_HEADLINE_TRUNCATED: ''
                }
            }
        )
    