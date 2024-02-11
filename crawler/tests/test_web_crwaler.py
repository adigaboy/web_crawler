import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from crawler.scraped_data_type import ScrapedDataType

from crawler.web_crawler.web_crawler import WebCrawlerWorker


class TestWebCrawler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        logger_mock = MagicMock()
        logger_mock.debug = MagicMock()
        logger_mock.error = MagicMock()
        self.web_crawler = WebCrawlerWorker(logger_mock)

    async def test_web_crawler__zero_depth(self):
        depth = 0
        res = await self.web_crawler.start_crawling('https://www.google.com', depth)
        self.assertEqual(res, [])

    @patch('aiohttp.ClientSession.get')
    async def test_web_crawler__one_depth(self, mock_get):
        depth = 1
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="/page1"></a><a href="www.example.com/page2"></a>')
        mock_get.return_value.__aenter__.return_value = mock_resp
        res = await self.web_crawler.start_crawling('https://www.example.com', depth)
        self.assertEqual(res, [ScrapedDataType('https://www.example.com', 1, 1)])

    @patch('aiohttp.ClientSession.get')
    async def test_web_crawler__crawled_url_in_response(self, mock_get):
        depth = 2
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(
            return_value='<a href="/page1"></a><a href="www.example.com"></a>'
        )
        mock_get.return_value.__aenter__.return_value = mock_resp
        res = await self.web_crawler.start_crawling('https://www.example.com', depth)
        self.assertEqual(
            res,
            [
                ScrapedDataType('https://www.example.com', 1, 1.0),
                ScrapedDataType('https://www.example.com/page1', 2, 1.0)
            ]
        )

    @patch('aiohttp.ClientSession.get')
    async def test_web_crawler__no_links_in_response(self, mock_get):
        depth = 2
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(
            return_value=''
        )
        mock_get.return_value.__aenter__.return_value = mock_resp
        res = await self.web_crawler.start_crawling('https://www.example.com', depth)
        self.assertEqual(res, [])
