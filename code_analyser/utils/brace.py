from dataclasses import dataclass
from typing import List, Tuple, Literal


@dataclass
class BraceConfig:
    style: Literal['K&R', 'Allman', 'Whitesmith']


@dataclass
class BraceReport:
    violations: List[Tuple[int, str]]  # (line number, line contents) tuple
