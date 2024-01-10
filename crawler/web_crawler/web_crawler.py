import asyncio
import aiohttp
from asyncio import gather
from bs4 import BeautifulSoup
from typing import List

from crawler.cache.cache import LocalCache
from crawler.utils import fix_url


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
        cached_links = self.local_cache.get_url_links(url)
        if cached_links:
            return cached_links

        retry = 0
        while retry < self.retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(url, timeout=1) as resp:
                        if 'Content-Type' in resp.headers and self.html_content_type_only not in resp.headers['Content-Type']:
                            return
                    async with session.get(url, timeout=1) as resp:
                        soup = BeautifulSoup(await resp.text(errors='ignore'), 'html.parser')
                        for element in soup.find_all('script'):
                            element.decompose()
                break
            except (aiohttp.ClientError, asyncio.TimeoutError):
                retry += 1
                self.logger.debug(f'Got connection error while trying to get {url}, on retry #{retry}')
        if retry == self.retries:
            self.logger.error(f'Got connection error while trying to get {url}')
            return
        elements = soup.find_all('a', {'href': True})
        links = [element.attrs['href'] for element in elements]
        return await self._add_domain_to_relative_urls(url, links)

    async def _add_domain_to_relative_urls(self, main_url: str, urls: List[str]) -> List[str]:
        updated_urls = []
        for url in urls:
            fixed_url = fix_url(url, main_url)
            if fixed_url:
                updated_urls.append(fixed_url)
        return updated_urls
