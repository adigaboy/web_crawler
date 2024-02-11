import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from crawler.web_crawler.web_crawler import WebCrawlerWorker


class TestExtractLinksFromPage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        logger_mock = MagicMock()
        logger_mock.debug = MagicMock()
        logger_mock.error = MagicMock()
        self.web_crawler = WebCrawlerWorker(logger_mock)

    @patch('aiohttp.ClientSession.head')
    @patch('aiohttp.ClientSession.get')
    async def test_extract_links_from_page_no_scheme(self, mock_get, mock_head):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="/page1"></a><a href="www.example.com/page2"></a>')
        mock_get.return_value.__aenter__.return_value = mock_resp

        mock_head_resp = MagicMock()
        mock_head_resp.headers = {'Content-Type': 'text/html'}
        mock_head.return_value.__aenter__.return_value = mock_head_resp
        links = await self.web_crawler._extract_links_from_page('https://www.example.com')
        
        self.assertEqual(links, ['https://www.example.com/page1', 'https://www.example.com/page2'])

    @patch('aiohttp.ClientSession.head')
    @patch('aiohttp.ClientSession.get')
    async def test_extract_links_from_page_remove_unwanted_elements_relative_url(self, mock_get, mock_head):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="/page1"></a><script>https://example.com/page2</script>')
        mock_get.return_value.__aenter__.return_value = mock_resp

        mock_head_resp = MagicMock()
        mock_head_resp.headers = {'Content-Type': 'text/html'}
        mock_head.return_value.__aenter__.return_value = mock_head_resp
        links = await self.web_crawler._extract_links_from_page('https://www.example.com')
        
        self.assertEqual(links, ['https://www.example.com/page1'])

    @patch('aiohttp.ClientSession.head')
    async def test_extract_links_from_page_page_not_html(self, mock_head):
        mock_head_resp = MagicMock()
        mock_head_resp.headers = {'Content-Type': 'script/lol'}
        mock_head.return_value.__aenter__.return_value = mock_head_resp
        links = await self.web_crawler._extract_links_from_page('https://example.com')
        
        self.assertEqual(links, [])

    @patch('aiohttp.ClientSession.head')
    @patch('aiohttp.ClientSession.get')
    async def test_extract_links_from_page_connection_error(self, mock_get, mock_head):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="https://example.com/page1"></a><script>https://example.com/page2</script>')
        mock_get.return_value.__aenter__.side_effect = asyncio.TimeoutError

        mock_head_resp = MagicMock()
        mock_head_resp.headers = {'Content-Type': 'text/html'}
        mock_head.return_value.__aenter__.return_value = mock_head_resp
        links = await self.web_crawler._extract_links_from_page('https://example.com')
        
        self.assertEqual(links, [])
        self.web_crawler.logger.debug.assert_called()
        self.assertEqual(self.web_crawler.logger.debug.call_count, 2)
        self.web_crawler.logger.error.assert_called_once()
