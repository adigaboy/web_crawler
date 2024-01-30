from queue import Queue
from typing import Any, List

from crawler.cache.cache import LocalCache
from crawler.cache.scraped_data_type import ScrapedDataType
from crawler.utils import get_url_domain


class RatioCalculator:
    """
    This module is in charge of calculating the url ratio in the page,
    according to the following logic:
    The ratio of the same domain links contained in the page, ranging from 0 to 1.
    """
    def __init__(self, ratio_calc_queue: Queue) -> None:
        self.ratio_calc_queue = ratio_calc_queue
        self.calculated_ratios = []

    async def calculate_ratios(self):
        while not self.ratio_calc_queue.empty():
            scraped_data: ScrapedDataType = await self.ratio_calc_queue.get()
            main_domain = get_url_domain(scraped_data.url)
            count = 0
            for link in scraped_data.links:
                url_domain = get_url_domain(link)
                if url_domain == main_domain:
                    count += 1
            ratio = count / len(scraped_data.links)
            self.calculated_ratios.append([scraped_data.url, scraped_data.depth, round(ratio, 2)])

    def get_calculated_ratios(self) -> List[List[Any]]:
        return self.calculated_ratios
