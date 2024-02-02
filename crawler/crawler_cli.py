from ssl import SSLError
import logging
from urllib.parse import urlparse
import requests
from crawler.exceptions import InvalidInputError

from crawler.file_generator.file_generator import FileResultGenerator
from crawler.web_crawler.web_crawler import WebCrawlerWorker


class CrawlerCLI:
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s-%(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S')
        self.logger = logging.getLogger('Web Crawler')
        self.web_crawler = WebCrawlerWorker(self.logger)
        self.file_response_generator = FileResultGenerator()

    async def run(self, url: str, depth: str):
        try:
            url, depth = self._validate_input(url, depth)
        except InvalidInputError as err:
            print(f"{bcolors.FAIL}Error: {str(err)}{bcolors.ENDC}")
            return
        self.logger.info(f'Starting crawling')
        results = await self.web_crawler.start_crawling(url, depth)
        output_filename = self.file_response_generator.generate_file_result(results)
        self.logger.info(f'{bcolors.OKGREEN}Done crawling {url}, results are in {output_filename} file{bcolors.ENDC}')

    def _validate_input(self, url: str, depth: str) -> None:
        try:
            depth = int(depth)
        except ValueError:
            raise InvalidInputError(f'Depth input {depth} must be of type integer')
        url_scheme = urlparse(url).scheme
        try:
            if not url_scheme:
                try:
                    resp = requests.head(f'http://{url}', timeout=1)
                    url = resp.url
                except SSLError:
                    resp = requests.head(f'https://{url}', timeout=1)
                    url = resp.url
            resp = requests.head(url, timeout=1)
            url = resp.url
        except requests.exceptions.ConnectionError:
            raise InvalidInputError(f'Url input {url} does not exists.')
        return url, depth

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
