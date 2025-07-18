from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class UnusedReport:
    unused_variables: List[Tuple[str, int]]
    unused_functions: List[Tuple[str, int]]
