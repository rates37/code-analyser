import ast
import io
import tokenize
from code_analyser.languages.base import LanguageAnalyser
from code_analyser.utils.identifiers import Identifiers
from code_analyser.utils.brace import BraceConfig, BraceReport
from code_analyser.utils.unused import UnusedReport
from typing import Optional


class PythonAnalyser(LanguageAnalyser):
    def _walk_with_parents(self, node: ast.AST, parent: Optional[ast.AST] = None):
        node.parent = parent
        yield node
        for child in ast.iter_child_nodes(node):
            yield from self._walk_with_parents(child, node)

    def parse(self, source: str) -> ast.AST:
        return ast.parse(source)

    def get_identifiers(self, ast_node: ast.AST) -> Identifiers:

        variables = set()
        functions = set()
        constants = set()  # dont' really exist in python, will return empty set for completeness
        classes = set()

        for node in ast.walk(ast_node):
            # variables are found in assign statements
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.add(target.id)
                    elif isinstance(target, (ast.Tuple, ast.List)):
                        for v in target.elts:
                            if isinstance(v, ast.Name):
                                variables.add(v.id)

            # all functions must be defined somewhere,
            #  so can find all function names by
            #  extracting all function definitions
            elif isinstance(node, ast.FunctionDef):
                functions.add(node.name)

            # same for classes as above:
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)

        return Identifiers(variables, functions, constants, classes)

    def check_brace_style(self, source: str, config: BraceConfig) -> BraceReport:
        # N/A for python
        return BraceReport([])

    def count_comments(self, ast_node: ast.AST, source: Optional[str] = None):
        # count comments with # (max 1 per line so just use a set):
        hash_comment_lines = set()
        if source is not None:
            try:
                for token in tokenize.generate_tokens(io.StringIO(source).readline):
                    if token.type == tokenize.COMMENT:
                        hash_comment_lines.add(token.start[0])
            except:  # ignore errors for now
                pass

        # Count docstrings:
        docstring_count = 0
        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    docstring_count += 1

        # count non-docstring multi-line strings:
        multiline_comment_count = 0
        for node in self._walk_with_parents(ast_node):
            # ast.Constant (new) == ast.Str (deprecated)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                # is only a docstring if is first statement in module, class, or function:
                parent = getattr(node, 'parent', None)
                is_docstring = False
                if parent and hasattr(parent, 'body') and parent.body:
                    if parent.body[0] is node:
                        is_docstring = True
                if not is_docstring:
                    multiline_comment_count += 1
        return len(hash_comment_lines) + docstring_count + multiline_comment_count

    def find_unused(self, ast_node: ast.AST) -> UnusedReport:
        declared_variables = {}
        used_variables = set()
        declared_functions = {}
        used_functions = set()

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        declared_variables[target.id] = node.lineno
                    elif isinstance(target, (ast.Tuple, ast.List)):
                        for v in target.elts:
                            if isinstance(v, ast.Name):
                                declared_variables[v.id] = node.lineno

            elif isinstance(node, ast.FunctionDef):
                declared_functions[node.name] = node.lineno

            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_variables.add(node.id)

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    used_functions.add(node.func.id)

        unused_variables = [(name, lineno) for name, lineno in declared_variables.items() if name not in used_variables]
        unused_functions = [(name, lineno) for name, lineno in declared_functions.items() if name not in used_functions]
        return UnusedReport(unused_variables, unused_functions)
