import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from crawler.web_crawler.web_crawler import _get_links_from_page


class TestGetLinksFromPage(unittest.IsolatedAsyncioTestCase):
    @patch('aiohttp.ClientSession.get')
    async def test_get_links_from_page_valid_url(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="https://example.com/page1"></a><a href="https://example.com/page2"></a>')
        mock_session.return_value.__aenter__.return_value = mock_resp

        links = await _get_links_from_page('https://example.com')

        self.assertEqual(links, ['https://example.com/page1', 'https://example.com/page2'])

    @patch('aiohttp.ClientSession.get')
    async def test_get_links_from_page_remove_unwanted_elements(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<a href="https://example.com/page1"></a><script>https://example.com/page1</script>')
        mock_session.return_value.__aenter__.return_value = mock_resp

        links = await _get_links_from_page('https://example.com')

        self.assertEqual(links, ['https://example.com/page1'])

    @patch('aiohttp.ClientSession.get')
    async def test_get_links_from_page_empty_links(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='<p>No links on this page</p>')
        mock_session.return_value.__aenter__.return_value = mock_resp

        links = await _get_links_from_page('https://example.com')

        self.assertEqual(links, [])

    @patch('aiohttp.ClientSession.get')
    async def test_get_links_from_page_timeout(self, mock_session):
        mock_session.return_value.__aenter__.side_effect = asyncio.TimeoutError

        with self.assertRaises(asyncio.TimeoutError):
            await _get_links_from_page('https://example.com')
