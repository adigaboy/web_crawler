import asyncio
from urllib.parse import urljoin
import aiohttp
from asyncio import gather
from bs4 import BeautifulSoup, Tag
from typing import List

from crawler.cache.cache import LocalCache
from crawler.utils import get_url_domain, get_url_scheme


class WebCrawler:
    """
    This module handles the main logic of crawling pages and extracting links.
    """
    crawled_urls: set
    max_depth: int
    retries = 3
    html_content_type_only = 'text/html'

    def __init__(self, local_cache: LocalCache, logger) -> None:
        self.local_cache = local_cache
        self.logger = logger
        self.crawled_urls = set()

    async def start_crawling(self, url: str, max_depth: int):
        self.crawled_urls.clear()
        self.max_depth = max_depth

        await self._rec_crawling(url, 1)
        return list(self.crawled_urls)

    async def _rec_crawling(self, url: str, curr_depth: int) -> None:
        if curr_depth > self.max_depth:
            return
        if url in self.crawled_urls:
            return
        links = await self._extract_links_from_page(url)
        if not links:
            return
        self.local_cache.set_url_links(url, links, curr_depth)
        self.crawled_urls.add(url)

        awaitables = []
        for link in links:
            coroutine = self._rec_crawling(link, curr_depth + 1)
            awaitables.append(coroutine)
        await gather(*awaitables)

    async def _extract_links_from_page(self, url: str) -> List[str]:
        retry = 0
        while retry < self.retries:
            try:
                if await self._check_if_page_is_html(url):    
                    links = await self._get_links_from_page(url) 
                    return self._add_domain_to_relative_urls(url, links)
                break
            except (aiohttp.ClientError, asyncio.TimeoutError):
                retry += 1
                self.logger.debug(f'Got connection error while trying to get {url}, on retry #{retry}')
        if retry == self.retries:
            self.logger.error(f'Got connection error while trying to get {url}')
            return

    def _add_domain_to_relative_urls(self, main_url: str, urls: List[str]) -> List[str]:
        updated_urls = []
        for url in urls:
            fixed_url = self._match_scheme_and_domain_like_main_url(url, main_url)
            if fixed_url:
                updated_urls.append(fixed_url)
        return updated_urls

    async def _check_if_page_is_html(self, url: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=1) as resp:
                if 'Content-Type' in resp.headers and self.html_content_type_only in resp.headers['Content-Type']:
                    return True
        return False

    async def _get_links_from_page(self, url: str) -> List[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=1) as resp:
                soup = BeautifulSoup(await resp.text(errors='ignore'), 'html.parser')
                self._remove_unwanted_elements(soup)
                elements = soup.find_all('a', {'href': True})
                links = [element.attrs['href'] for element in elements]
                return links

    def _remove_unwanted_elements(self, soup: Tag) -> None:
        for element in soup.find_all('script'):
            element.decompose()

    def _match_scheme_and_domain_like_main_url(self, url: str, main_url: str) -> str:
        url = self._add_scheme_to_url(url, main_url)
        url = self._add_doamin_to_url(url, main_url)
        return url

    @staticmethod
    def _add_scheme_to_url(url: str, main_url: str) -> str:
        scheme = get_url_scheme(url)
        if not scheme:
            url = urljoin(main_url, url)
        elif scheme not in ['https', 'http']:
            return None
        return url

    @staticmethod
    def _add_doamin_to_url(url: str, main_url: str) -> str:
        domain = get_url_domain(url)
        if domain == '':
            url = urljoin(main_url, url)
        return url
