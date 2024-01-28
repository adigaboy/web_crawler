import csv
from typing import List
from crawler.cache.cache import LocalCache
from crawler.cache.scraped_data_type import ScrapedDataType


class FileResultGenerator:
    """
    This module is in charge of writing the results of the web crawler into TSV file.
    """
    def __init__(self, local_cache: LocalCache) -> None:
        self.local_cache = local_cache
        self.filename = 'result.tsv'
        self.headers = ['url', 'depth', 'ratio']

    def generate_file_result(self, urls: List[str]):
        data_for_file: List[ScrapedDataType] = []
        for url in urls:
            url_data = self.local_cache.get_url_data(url)
            data_for_file.append(url_data)
        data_for_file.sort(key=lambda data: data.depth)
        with open(self.filename, mode='w', newline='') as result_file:
            csv_writer = csv.writer(result_file, delimiter='\t')
            csv_writer.writerow(self.headers)
            for data in data_for_file:
                csv_writer.writerow(data.to_output_list())
        return self.filename
