from ssl import SSLError
import logging
import requests

from crawler.cache.cache import LocalCache
from crawler.file_generator.file_generator import FileResultGenerator
from crawler.ratio_calculator.ratio_calculator import RatioCalculator
from crawler.utils import get_url_scheme
from crawler.web_crawler.web_crawler import WebCrawler


class CrawlerCLI:
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s-%(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S')
        self.logger = logging.getLogger('Web Crawler')
        local_cache = LocalCache()
        self.web_crawler = WebCrawler(local_cache, self.logger)
        self.ratio_calculator = RatioCalculator(local_cache)
        self.file_response_generator = FileResultGenerator(local_cache)

    async def run(self, url: str, depth: str):
        url, depth = self.validate_input(url, depth)
        self.logger.info(f'Starting crawling')
        extracted_urls = await self.web_crawler.start_crawling(url, depth)
        self.logger.info(f'Starting ratio calculation')
        self.ratio_calculator.calculate_ratios(extracted_urls)
        self.logger.info(f'Writing to file')
        output_filename = self.file_response_generator.generate_file_result(extracted_urls)
        self.logger.info(f'Done crawling {url}, results are in {output_filename} file')

    def validate_input(self, url: str, depth: str) -> None:
        try:
            depth = int(depth)
        except ValueError:
            raise Exception(f'Depth input {depth} must be of type integer')
        url_scheme = get_url_scheme(url)
        try:
            if not url_scheme:
                try:
                    resp = requests.head(f'http://{url}', timeout=1)
                    url = resp.url
                except SSLError:
                    resp = requests.head(f'https://{url}', timeout=1)
                    url = resp.url
        except ConnectionError:
            raise Exception(f'Url input {url} does not exists.')
        return url, depth
