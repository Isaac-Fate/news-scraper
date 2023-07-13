from typing import Self, Optional
from bson import ObjectId

# fields of interest
DATE = 'date'
PUBLICATION = 'publication'
HEADLINE = 'headline'
LINK = 'link'
FIELDS_OF_INTEREST = [
    DATE,
    PUBLICATION,
    HEADLINE,
    LINK
]

class News(dict):
    
    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)
        
        self._id: Optional[ObjectId] = None
    
    @property
    def id(self) -> Optional[ObjectId]:
        return self._id
    
    @classmethod
    def from_document(cls, document: dict) -> Self:
        
        # extract the ID
        news_id = document.pop('_id')
        
        # create a news instance
        news = cls(document)
        
        # set the ID
        news._id = news_id
        
        return news
        
    