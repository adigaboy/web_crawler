from typing import Dict, List

from crawler.cache.scraped_data_type import ScrapedDataType


class LocalCache:
    """
    This module is in charge of local cache of Urls.
    A key-value database.
    
    Key:
        url - string, the page url
    Value:
        ScrapedDataType:
            url - string, the page url
            links - List[string], the links contained in the page
            depth - int, the depth position of the page
            ratio - int, the calculated ratio of the url.
    """
    data: Dict[str, ScrapedDataType]

    def __init__(self) -> None:
        self.data = {}

    def get_url_data(self, url: str) -> ScrapedDataType:
        return self.data[url]

    def get_url_links(self, url: str) -> List[str] | None:
        url_data = self.data.get(url)
        return url_data.links if url_data else None

    def get_url_ratio(self, url: str) -> int | None:
        url_data = self.data.get(url)
        return url_data.ratio if url_data else None

    def set_url_links(self, url: str, links: List[str], depth: int) -> None:
        if url not in self.data:
            self.data[url] = ScrapedDataType(links, 0, depth)
        else:
            self.data[url].links = links

    def set_url_ratio(self, url: str, ratio: int) -> None:
        self.data[url].ratio = ratio
