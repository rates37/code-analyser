from abc import ABC, abstractmethod
from typing import Any, Optional
from code_analyser.utils.identifiers import Identifiers
from code_analyser.utils.brace import BraceConfig, BraceReport
from code_analyser.utils.unused import UnusedReport


class LanguageAnalyser(ABC):
    @abstractmethod
    def parse(self, source: str) -> Any:
        """Parse the source code and return an AST or other intermediate representation

        Args:
            source (str): The source code as a string

        Returns:
            Any: An AST or language-specific parse tree
        """
        pass

    @abstractmethod
    def get_identifiers(self, ast: Any) -> Identifiers:
        """Extract all identifiers (variables, functions, constants, classes) from the AST representation of source code.

        Args:
            ast (Any): The AST or intermediate representation

        Returns:
            Identifiers: Contains sets of variable names, function names, constants, and class names.
        """
        pass

    @abstractmethod
    def check_brace_style(self, source: str, config: BraceConfig) -> Optional[BraceReport]:
        """Check the brace style of the source code against the given configuration.

        Args:
            source (str): The source code as a string
            config (BraceConfig): A BraceConfig object specifying the desired style

        Returns:
            Optional[BraceReport]: A BraceReport with any violations found, or None if not applicable (e.g., Python)
        """
        pass

    @abstractmethod
    def count_comments(self, ast: Any, source: Optional[str] = None) -> int:
        """Count the number of comments in the code (single-line, multi-line, docstrings, etc.).

        Args:
            ast (Any): The AST or intermediate representation (may be ignored for some languages)
            source (Optional[str], optional): The source code as a string (optional, but may be required for some languages). Defaults to None.

        Returns:
            int: The total number of comments found
        """
        pass

    @abstractmethod
    def find_unused(self, ast: Any) -> UnusedReport:
        """Find unused variables and functions in the code.

        Args:
            ast (Any): The AST or intermediate representation

        Returns:
            UnusedReport: An UnusedReport listing unused variables and functions.
        """
        pass
