from typing import Self, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

CHROME_OPTIONS = webdriver.ChromeOptions()

# do not display the window
CHROME_OPTIONS.add_argument('--headless')

class WebDriver(webdriver.Chrome):
    
    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)
        
        self._service: Optional[Service] = None
    
    def __str__(self) -> str:
        return f'Chrome web driver on port: {self.port}'
    
    def __repr__(self):
        return str(self)
    
    @property
    def port(self) -> int:
        
        return self._service.port
        
    @classmethod
    def on_port(cls, port: int = 0) -> Self:
        
        service = Service(
            ChromeDriverManager().install(),
            port=port
        )
        
        driver = cls(
            service=service,
            options=CHROME_OPTIONS
        )
        
        driver._service = service
        
        return driver
    
    def get_html(self, url: str) -> str:
        
        # load the web page
        self.get(url)
        
        # raw HTML of the page
        html = self.page_source
        
        return html
    
    
    