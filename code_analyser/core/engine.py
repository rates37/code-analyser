import os
from typing import Union, Optional, Dict, Type
from code_analyser.languages.base import LanguageAnalyser
from code_analyser.utils.brace import BraceConfig, BraceReport
from code_analyser.utils.identifiers import Identifiers
from code_analyser.utils.unused import UnusedReport
from code_analyser.languages.python import PythonAnalyser
from code_analyser.languages.java import JavaAnalyser
from pathlib import Path
from dataclasses import dataclass


LANGUAGE_MAP = {
    ".py": PythonAnalyser,
    ".java": JavaAnalyser
}


@dataclass
class AnalyserResult:
    identifiers: Identifiers
    brace_report: Optional[BraceReport]
    comment_count: int
    unused_report: UnusedReport


class AnalyserEngine:
    language_map: Dict[str, Type[LanguageAnalyser]]

    def __init__(self) -> None:
        self.language_map = LANGUAGE_MAP

    def analyse_file(self, filepath: Union[str, Path], brace_config: Optional[BraceConfig] = None) -> AnalyserResult:
        """Analyse a source file and return an AnalyserResult

        Args:
            filepath (Union[str, Path]): Path to the source file
            brace_config (Optional[BraceConfig], optional): Optional brace style config. Defaults to None.

        Returns:
            AnalyserResult: Contains identifiers, brace report, comment count, and unused attributes report
        """
        pass
