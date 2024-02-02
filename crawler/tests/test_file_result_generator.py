import os
from unittest import TestCase

from crawler.file_generator.file_generator import FileResultGenerator
from crawler.tests.mock import generate_results

class TestFileResultGenerator(TestCase):
    def setUp(self):
        self.file_generator = FileResultGenerator()
        self.results = generate_results()
        self.is_file_created = False
        self.result_file_path = './crawler/tests/expected_result_file.tsv'

    def tearDown(self) -> None:
        self._compare_files()
        if self.is_file_created:
            os.remove(self.file_generator.filename)
        self.is_file_created = False
        return super().tearDown()

    def _compare_files(self):
        with open(self.file_generator.filename, 'r') as result_file:
            result_lines = result_file.readlines()
        with open(self.result_file_path, 'r') as expected_file:
            expected_lines = expected_file.readlines()
        self.assertListEqual(result_lines, expected_lines)

    def test_generate_result_file(self):
        self.file_generator.generate_file_result(self.results)
        self.is_file_created = True
