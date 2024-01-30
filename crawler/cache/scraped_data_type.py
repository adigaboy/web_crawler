
from dataclasses import dataclass
from typing import Any, List


@dataclass
class ScrapedDataType:
    """
    Dataclass stored in the local cache database.
    """
    links: List[str]
    ratio: int
    depth: int

    def to_list(self) -> List[Any]:
        return [self.depth, self.ratio]
