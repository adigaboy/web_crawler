
from typing import Any, List


class ScrapedDataType:
    """
    Class of data stored in the local cache database.
    """
    url: str
    links: List[str]
    ratio: int
    depth: int

    def __init__(self, url: str, links: List[str]=None, ratio: int=None, depth: int=None) -> None:
        self.url = url
        self.links = links
        self.ratio = ratio
        self.depth = depth

    def to_output_list(self) -> List[Any]:
        return [self.url, self.depth, self.ratio]
