import unittest
from unittest.mock import patch
from crawler.web_crawler.web_crawler import _calculate_ratios


class TestCalculateRatios(unittest.IsolatedAsyncioTestCase):

    async def test_calculate_ratios_with_same_domain(self):
        url = "https://example.com"
        links = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        result = await _calculate_ratios(url, links)
        self.assertEqual(result, 1.0)

    async def test_calculate_ratios_with_different_domains(self):
        url = "https://example.com"
        links = ["https://anotherdomain.com/page1", "https://anotherdomain.com/page2", "https://anotherdomain.com/page3"]
        result = await _calculate_ratios(url, links)
        self.assertEqual(result, 0.0)

    async def test_calculate_ratios_with_mixed_domains(self):
        url = "https://example.com"
        links = ["https://example.com/page1", "https://anotherdomain.com/page2", "https://example.com/page3"]
        result = await _calculate_ratios(url, links)
        self.assertEqual(result, 0.67)

    async def test_calculate_ratios_with_empty_links(self):
        url = "https://example.com"
        links = []
        result = await _calculate_ratios(url, links)
        self.assertEqual(result, 0.0)  # Empty links list should result in a ratio of 0.0
