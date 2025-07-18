from dataclasses import dataclass
from typing import Set


@dataclass
class Identifiers:
    variables: Set[str]
    functions: Set[str]
    constants: Set[str]
    classes: Set[str]
