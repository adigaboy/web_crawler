import csv
from typing import List

from crawler.scraped_data_type import ScrapedDataType


class FileResultGenerator:
    """
    This module is in charge of writing the results of the web crawler into TSV file.
    """
    def __init__(self) -> None:
        self.filename = 'result.tsv'
        self.headers = ['url', 'depth', 'ratio']

    def generate_file_result(self, calculated_ratios: List[ScrapedDataType]):
        calculated_ratios.sort(key=lambda data: data.depth)
        with open(self.filename, mode='w', newline='') as result_file:
            csv_writer = csv.writer(result_file, delimiter='\t')
            csv_writer.writerow(self.headers)
            for data in calculated_ratios:
                csv_writer.writerow(data.to_list())
        return self.filename
