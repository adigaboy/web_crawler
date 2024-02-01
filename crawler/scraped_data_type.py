from dataclasses import dataclass
from typing import Any, List


@dataclass
class ScrapedDataType:
    url: str
    depth: int
    ratio: float

    def to_list(self) -> List[Any]:
        return [self.url, self.depth, self.ratio]
