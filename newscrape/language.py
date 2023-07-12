from typing import Self
from enum import Enum

class Language(Enum):
    
    English = 'en'
    Chinese = 'zh'
    
    @classmethod
    def from_str(cls, language: str) -> Self:
        
        # convert to lower case
        language = language.lower()
        
        if language in {'en', 'english'}:
            return cls.English
        
        elif language in {'zh', 'chinese'}:
            return cls.Chinese
        
        else:
            raise ValueError('unknown language')
        
    def to_url_query_value(self) -> str:
        
        match self:
            
            case Language.English:
                return 'lang_en'
            
            case Language.Chinese:
                return 'lang_zh-CN'
            