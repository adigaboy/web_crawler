
from ssl import SSLError
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import requests

from crawler.crawler_cli import CrawlerCLI
from crawler.exceptions import InvalidInputError
from crawler.scraped_data_type import ScrapedDataType
from crawler.web_crawler.web_crawler import WebCrawlerWorker

def mock_https_only_site(url, timeout):
    if url.startswith('http://'):
        raise SSLError('BOOM')
    
    mock_head_resp = MagicMock()
    mock_head_resp.url = url
    return mock_head_resp

class TestCLIValidateInput(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        logger_mock = MagicMock()
        logger_mock.debug = MagicMock()
        logger_mock.error = MagicMock()
        self.cli = CrawlerCLI()
        self.cli.logger = logger_mock
        self.cli.web_crawler = WebCrawlerWorker(logger_mock)

    async def test_bad_depth_input(self):
        url = 'https://www.google.com'
        depth = 'asd'

        self.assertRaises(InvalidInputError, self.cli._validate_input, url, depth)

    @patch('requests.head')
    async def test_bad_url_input(self, mock_head):
        url = 'gggggg'
        depth = 1
        mock_head.side_effect = requests.exceptions.ConnectionError('hello')

        self.assertRaises(InvalidInputError, self.cli._validate_input, url, depth)

    @patch('requests.head')
    async def test_positive_input(self, mock_head):
        url = 'https://www.example.com'
        depth = 1
        
        mock_head_resp = MagicMock()
        mock_head_resp.headers = {'Content-Type': 'text/html'}
        mock_head_resp.url = url
        mock_head.return_value = mock_head_resp

        res = self.cli._validate_input(url, depth)
        self.assertEqual(res, (url, depth))

    @patch('requests.head')
    async def test_positive_input__no_scheme(self, mock_head):
        url = 'www.example.com'
        depth = 1
        expected_url = f'http://{url}'

        mock_head_resp = MagicMock()
        mock_head_resp.url = expected_url
        mock_head.return_value = mock_head_resp

        res = self.cli._validate_input(url, depth)
        self.assertEqual(res, (expected_url, depth))

    @patch('requests.head', mock_https_only_site)
    async def test_positive_input__no_scheme_https(self):
        url = 'www.example.com'
        depth = 1
        expected_url = f'https://{url}'

        res = self.cli._validate_input(url, depth)
        self.assertEqual(res, (expected_url, depth))


class TestCLIRun(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        logger_mock.error = MagicMock()
        self.cli = CrawlerCLI()
        self.cli.logger = logger_mock
        self.cli.web_crawler = WebCrawlerWorker(logger_mock)

    @patch('requests.head')
    async def test_run__bad_input(self, mock_head):
        url = 'gggggg'
        depth = 1
        mock_head.side_effect = requests.exceptions.ConnectionError('hello')

        await self.cli.run(url, depth)
        self.cli.logger.error.assert_called_once()

    @patch('requests.head')
    async def test_run__positive(self, mock_head):
        url = 'https://www.example.com'
        depth = 1
        mock_head_resp = MagicMock()
        mock_head_resp.url = url
        mock_head.return_value = mock_head_resp
        self.cli.web_crawler.start_crawling = AsyncMock(reutrn_value=[ScrapedDataType(url, 1, 1.0)])
        self.cli.file_response_generator.generate_file_result = MagicMock(return_value='result.tsv')

        await self.cli.run(url, depth)
        self.cli.logger.info.assert_called()
