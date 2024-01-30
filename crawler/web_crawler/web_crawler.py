import asyncio
from asyncio import events
import logging
from urllib.parse import urljoin
import aiohttp
from asyncio import gather
from bs4 import BeautifulSoup, Tag
from typing import Any, List

from crawler.cache.cache import LocalCache
from crawler.cache.scraped_data_type import ScrapedDataType
from crawler.utils import get_url_domain, get_url_scheme

logger = logging.getLogger()
html_content_type_only = 'text/html'


class WebCrawlerWorker:
    """
    This module handles the main logic of crawling pages and extracting links.
    """
    crawled_urls: set
    max_depth: int
    retries = 2

    def __init__(
            self,
            ratio_calc_queue: asyncio.Queue,
            logger
        ) -> None:
        self.ratio_calc_queue = ratio_calc_queue
        self.logger = logger
        self.crawled_urls = set()

    async def start_crawling(
            self,
            main_url: str,
            max_depth: int
        ):
        results = []
        tasks = []
        crawling_queue = asyncio.Queue()
        await crawling_queue.put((main_url, 1))
        for _ in range(25):
            task = asyncio.create_task(worker(
                crawling_queue,
                self.ratio_calc_queue,
                results,
                self.crawled_urls,
                max_depth
            ))
            tasks.append(task)

        await crawling_queue.join()  # Wait for all tasks in the queue to be processed

        for task in tasks:
            task.cancel()  # Stop the tasks

        return list(set(results))

async def worker(queue: asyncio.Queue, ratio_calc_queue, results, visited, max_depth):
    while True:
        current_url, current_depth = await queue.get()
        if current_depth > max_depth or current_url in visited:
            queue.task_done()
            continue

        visited.add(current_url)
        links = await _extract_links_from_page(current_url, 3)
        if not links:
            queue.task_done()
            continue
        results.append((current_url, current_depth))

        for link in links:
            await queue.put((link, current_depth + 1))
        await ratio_calc_queue.put(ScrapedDataType(current_url, links, current_depth))

        queue.task_done()

async def _extract_links_from_page(url: str, retries: int) -> List[str]:
    retry = 0
    while retry < retries:
        try:
            if await _check_if_page_is_html(url):    
                links = await _get_links_from_page(url) 
                return _add_domain_to_relative_urls(url, links)
            break
        except (aiohttp.ClientError, asyncio.TimeoutError):
            retry += 1
            logger.debug(f'Got connection error while trying to get {url}, on retry #{retry}')
    if retry == retries:
        logger.error(f'Got connection error while trying to get {url}')
        return

def _add_domain_to_relative_urls(main_url: str, urls: List[str]) -> List[str]:
    updated_urls = []
    for url in urls:
        fixed_url = _match_scheme_and_domain_like_main_url(url, main_url)
        if fixed_url:
            updated_urls.append(fixed_url)
    return updated_urls

async def _check_if_page_is_html(url: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.head(url, timeout=1) as resp:
            if 'Content-Type' in resp.headers and html_content_type_only in resp.headers['Content-Type']:
                return True
    return False

async def _get_links_from_page(url: str) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=1) as resp:
            soup = BeautifulSoup(await resp.text(errors='ignore'), 'html.parser')
            _remove_unwanted_elements(soup)
            elements = soup.find_all('a', {'href': True})
            links = [element.attrs['href'] for element in elements]
            return links

def _remove_unwanted_elements(soup: Tag) -> None:
    for element in soup.find_all('script'):
        element.decompose()

def _match_scheme_and_domain_like_main_url(url: str, main_url: str) -> str:
    url = _add_scheme_to_url(url, main_url)
    url = _add_doamin_to_url(url, main_url)
    return url

def _add_scheme_to_url(url: str, main_url: str) -> str:
    scheme = get_url_scheme(url)
    if not scheme:
        url = urljoin(main_url, url)
    elif scheme not in ['https', 'http']:
        return None
    return url

def _add_doamin_to_url(url: str, main_url: str) -> str:
    domain = get_url_domain(url)
    if domain == '':
        url = urljoin(main_url, url)
    return url
