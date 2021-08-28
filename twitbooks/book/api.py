from typing import Protocol, Optional
from abc import abstractmethod
import requests


class BookInfo:
    def __init__(self, title: str, link: str, image_link: Optional[str]):
        self.title = title
        self.link = link
        self.image_link = image_link

    def __str__(self):
        return "title = {}, link= {}, image_link = {}".format(self.title, self.link, self.image_link)


class BookApi(Protocol):
    @abstractmethod
    def get_info(self, title: str) -> Optional[BookInfo]:
        raise NotImplemented


class _GoogleBooksApi(BookApi):
    def get_info(self, title: str) -> Optional[BookInfo]:
        params = {"q": title, "langRestrict": "en", "maxResults": 1}
        r = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
        if r.status_code != 200:
            return None
        payload = r.json()
        if 'items' not in payload:
            return None
        items = payload['items']
        if len(items) == 0:
            return None
        volume_info = items[0]['volumeInfo']
        image_link = None
        if 'imageLinks' in volume_info:
            image_link = volume_info['imageLinks']['thumbnail']
        return BookInfo(
            title=volume_info['title'],
            link=volume_info['infoLink'],
            image_link=image_link
        )


def new() -> BookApi:
    return _GoogleBooksApi()
