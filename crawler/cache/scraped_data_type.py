
from dataclasses import dataclass
from typing import Any, List


@dataclass
class ScrapedDataType:
    """
    Dataclass stored in the local cache database.
    """
    url: str
    links: List[str]
    depth: int
