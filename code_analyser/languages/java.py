from code_analyser.languages.base import LanguageAnalyser
from code_analyser.utils.identifiers import Identifiers
from code_analyser.utils.brace import BraceConfig, BraceReport
from code_analyser.utils.unused import UnusedReport
import re
import javalang
import javalang.tree
import warnings


class JavaAnalyser(LanguageAnalyser):
    def parse(self, source: str) -> javalang.tree.CompilationUnit:
        return javalang.parse.parse(source)

    def get_identifiers(self, ast_node: javalang.tree.CompilationUnit):
        variables = set()
        functions = set()
        constants = set()
        classes = set()

        for _, node in ast_node:
            if isinstance(node, javalang.tree.ClassDeclaration):
                classes.add(node.name)
            elif isinstance(node, javalang.tree.MethodDeclaration):
                functions.add(node.name)
            elif isinstance(node, javalang.tree.VariableDeclarator):
                variables.add(node.name)
            elif isinstance(node, javalang.tree.FieldDeclaration):
                # check if it's constant:
                is_constant = any('final' in str(mod)
                                  for mod in getattr(node, 'modifiers', []) or [])
                for decl in getattr(node, 'declarators', []):
                    if is_constant:
                        constants.add(decl.name)
                    else:
                        variables.add(decl.name)
        return Identifiers(variables, functions, constants, classes)

    def check_brace_style(self, source: str, config: BraceConfig) -> BraceReport:
        # this is wip and very buggy
        warnings.warn(
            "This function is a Work In Progress and may change, produce incorrect results or be removed entirely.",
            category=UserWarning,
            stacklevel=2
        )
        violations = []
        lines = source.splitlines()
        style = config.style if config else BraceConfig('K&R').style

        for i, line in enumerate(lines):
            stripped = line.strip()

            if '{' in stripped:
                prev = lines[i-1].strip() if i > 0 else ''
                if style == 'K&R':
                    # { should be on same line as control statement/method
                    if stripped == '{':
                        violations.append(
                            (i+1, f'Brace should be on same line ({style})'))
                elif style == 'Allman':
                    # { should be on its own line
                    if stripped != '{':
                        violations.append(
                            (i+1, f'Brace should be on its own line ({style})'))
                elif style == 'Whitesmith':
                    # { should be on its own line and indented (ew)
                    if stripped != '{' or (line and not (line.startswith(' ') or line.startswith('\t'))):
                        violations.append(
                            (i+1, f'Brace should be indented on its own line ({style})'))
        return BraceReport(violations)

    def count_comments(self, ast: javalang.tree.CompilationUnit, source: str) -> int:
        if not source:
            return 0
        single_line_comment_count = 0
        multi_line_comment_count = 0
        in_string = False
        escape_next = False
        for line in source.splitlines():
            i = 0
            while i < len(line):
                ch = line[i]

                if escape_next:
                    escape_next = False
                    i += 1
                    continue

                if ch == '\\':
                    escape_next = True
                    i += 1
                    continue

                if ch == '"':
                    in_string = not in_string
                    i += 1
                    continue

                if not in_string and line[i:i+2] == '//':
                    single_line_comment_count += 1
                    break

                if not in_string and line[i:i+2] == '/*':
                    multi_line_comment_count += 1
                    # skip to end of multilie comment
                    while i < len(line) and line[i:i+2] != '*/':
                        i += 1
                    if i < len(line):
                        i += 2
                    continue
                i += 1

        return single_line_comment_count + multi_line_comment_count

    def find_unused(self, ast_node: javalang.tree.CompilationUnit) -> UnusedReport:
        declared_variables = {}
        used_variables = set()
        declared_functions = {}
        used_functions = set()

        for _, node in ast_node:
            if isinstance(node, javalang.tree.VariableDeclarator):
                pos = getattr(node, 'position', None)
                declared_variables[node.name] = pos[0] if pos and isinstance(
                    pos, tuple) else 0
            elif isinstance(node, javalang.tree.MethodDeclaration):
                pos = getattr(node, 'position', None)
                declared_functions[node.name] = pos[0] if pos and isinstance(
                    pos, tuple) else 0
            elif isinstance(node, javalang.tree.MemberReference):
                used_variables.add(node.member)
            elif isinstance(node, javalang.tree.MethodInvocation):
                used_functions.add(node.member)

        unused_variables = [(name, lineno) for name, lineno in declared_variables.items(
        ) if name not in used_variables]
        unused_functions = [(name, lineno) for name, lineno in declared_functions.items(
        ) if name not in used_functions]
        return UnusedReport(unused_variables, unused_functions)
