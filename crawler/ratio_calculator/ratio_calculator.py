from typing import List

from crawler.cache.cache import LocalCache
from crawler.utils import get_url_domain


class RatioCalculator:
    """
    This module is in charge of calculating the url ratio in the page,
    according to the following logic:
    The ratio of the same domain links contained in the page, ranging from 0 to 1.
    """
    def __init__(self, local_cache: LocalCache) -> None:
        self.local_cache = local_cache

    def calculate_ratios(self, urls: List[str]):
        for url in urls:
            url_links = self.local_cache.get_url_links(url)
            main_domain = get_url_domain(url)
            count = 0
            for link in url_links:
                url_domain = get_url_domain(link)
                if url_domain == main_domain:
                    count += 1
            ratio = count / len(url_links)
            self.local_cache.set_url_ratio(url, round(ratio, 2))
