from typing import Optional
import re
from bs4 import BeautifulSoup, Tag
from .picker import NewsHeadlinePicker

HEADER_TAG_NAME_RE = re.compile(r'^h1$')

def find_news_headline_from_news_post_html(
        html: str | bytes,
        picker: Optional[NewsHeadlinePicker] = None
    ) -> Optional[str]:
    
    # make soup
    soup = BeautifulSoup(html, features='lxml')
    
    # all header tags
    header_tags = soup.find_all(name=HEADER_TAG_NAME_RE)
    
    # all header texts
    header_texts = []
    tag: Tag
    for tag in header_tags:
        if tag.text is not None:
            header_texts.append(tag.text)

    # no headline is found
    if len(header_texts) == 0:
        return None
    
    # there is one and only one possible headline
    if len(header_texts) == 1:
        headline = header_texts[0]
        return headline
    
    # return None when no picker is provided
    if picker is None: return None
    
    # pick one headline
    headline = picker.pick(headlines=header_texts)
    
    return headline
    
__all__ = [
    'find_news_headline_from_news_post_html',
    'NewsHeadlinePicker'
]
