from typing import Self, Optional
import os
from pathlib import Path
import tomllib
from xpyutils import lazy_property, singleton

@singleton
class ProjectConfig:
    
    def __init__(self) -> None:
        
        self._data: Optional[dict] = None
        
    @classmethod
    def load(cls, filepath: os.PathLike) -> Self:
        
        # the one and only configuration instance
        config = cls()
        
        # load config from file path
        with open(filepath, 'rb') as f:
            config._data = tomllib.load(f)
            
        # put OpenAI API key into the environment
        os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY
    
    @lazy_property
    def OPENAI_API_KEY(self) -> str:
        
        return self._data.pop('openai-api-key')
    
    @lazy_property
    def MONGODB(self) -> dict:
        
        return self._data.pop('mongodb')
    
    @lazy_property
    def MONGODB_DATABASE_NAME(self) -> str:
        
        return self.MONGODB['database-name']
        
    @lazy_property
    def MONGODB_HOST(self) -> str:
        
        return self.MONGODB['host']
    
    @lazy_property
    def MONGODB_PORT(self) -> int:
        
        return self.MONGODB['port']
    
CONFIG = ProjectConfig()
