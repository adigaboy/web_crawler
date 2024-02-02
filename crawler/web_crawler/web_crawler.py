import asyncio
import logging
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup, Tag
from typing import Any, Dict, List

from crawler.scraped_data_type import ScrapedDataType

logger = logging.getLogger()


class WebCrawlerWorker:
    """
    This module crawls the links in the main url, extarct them and
    calculates the ratio of them.
    """
    crawled_urls: set
    max_depth: int
    retries = 2

    def __init__(self, logger) -> None:
        self.results = []
        self.crawling_queue = asyncio.Queue()
        self.crawled_urls = set()
        self.logger = logger

    async def start_crawling(
            self,
            main_url: str,
            max_depth: int
        ) -> List[ScrapedDataType]:
        crawler_tasks = []
        await self.crawling_queue.put((main_url, 1))
        for _ in range(150):
            task = asyncio.create_task(self._wroker(
                max_depth
            ))
            crawler_tasks.append(task)

        await self.crawling_queue.join()  # Wait for all tasks in the queue to be processed

        for task in crawler_tasks:
            task.cancel()  # Stop the tasks

        return self.results

    async def _wroker(self, max_depth: int) -> None:
        while True:
            current_url, current_depth = await self.crawling_queue.get()
            if current_url in self.crawled_urls:
                self.crawling_queue.task_done()
                continue
            self.crawled_urls.add(current_url)

            links = await self._extract_links_from_page(current_url)
            if not links:
                self.crawling_queue.task_done()
                continue
            ratio = await _calculate_ratios(current_url, links)
            self.results.append(ScrapedDataType(current_url, current_depth, ratio))

            if current_depth + 1 <= max_depth:
                for link in links:
                    await self.crawling_queue.put((link, current_depth + 1))

            self.crawling_queue.task_done()

    async def _extract_links_from_page(self, url: str) -> List[str]:
        retry = 0
        while retry < self.retries:
            try:
                if await _check_if_page_is_html(url):    
                    links = await _get_links_from_page(url) 
                    return _get_absolute_urls(url, links)
                break
            except (aiohttp.ClientError, asyncio.TimeoutError):
                retry += 1
                logger.debug(f'Got connection error while trying to get {url}, on retry #{retry}')
        if retry == self.retries:
            logger.error(f'Got connection error while trying to get {url}')

def _get_absolute_urls(main_url: str, urls: List[str]) -> List[str]:
    updated_urls = []
    for url in urls:
        absolute_url = _match_scheme_and_domain_like_main_url(url, main_url)
        if absolute_url:
            updated_urls.append(absolute_url)
    return updated_urls

async def _check_if_page_is_html(url: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.head(url, timeout=1) as resp:
            if 'Content-Type' in resp.headers and 'text/html' in resp.headers['Content-Type']:
                return True
    return False

async def _get_links_from_page(url: str) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=1) as resp:
            soup = BeautifulSoup(await resp.text(errors='ignore'), 'html.parser')
            _remove_unwanted_elements(soup)
            return _extract_links_from_soup(soup)

def _remove_unwanted_elements(soup: Tag) -> None:
    for element in soup.find_all('script'):
        element.decompose()

def _extract_links_from_soup(soup: Tag) -> None:
    elements = soup.find_all('a', {'href': True})
    return [element.attrs['href'] for element in elements]

def _match_scheme_and_domain_like_main_url(url: str, main_url: str) -> str:
    url = _add_scheme_to_url(url, main_url)
    url = _add_doamin_to_url(url, main_url)
    return url

def _add_scheme_to_url(url: str, main_url: str) -> str:
    scheme = urlparse(url).scheme
    if not scheme:
        url = urljoin(main_url, url)
    elif scheme not in ['https', 'http']:
        return None
    return url

def _add_doamin_to_url(url: str, main_url: str) -> str:
    domain = urlparse(url).netloc
    if domain == '':
        url = urljoin(main_url, url)
    return url

async def _calculate_ratios(url: str, links: List[str]):
    main_domain = urlparse(url).netloc
    count = 0
    for link in links:
        url_domain = urlparse(url).netloc
        if url_domain == main_domain:
            count += 1
    ratio = count / len(links)
    return round(ratio, 2)
