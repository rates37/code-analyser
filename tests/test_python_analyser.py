from code_analyser.languages.python import PythonAnalyser
from pathlib import Path
from code_analyser.core.engine import AnalyserEngine

def test_python_identifiers():
    source = '''

def foo():
    x = 1
    y = 2
    return x + y

class Bar:
    pass
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    ids = analyser.get_identifiers(ast_node)
    assert 'foo' in ids.functions
    assert 'Bar' in ids.classes
    assert 'x' in ids.variables
    assert 'y' in ids.variables


def test_python_comment_count():
    analyser = PythonAnalyser()
    source = '''
# This is a comment
def foo():
    """Docstring"""
    x = 1 # Inline comment
    # comment with a # in it
    return x

"""multiline comment (not docstring)"""

my_string = """multiline string

not a comment"""
'''
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 5


def test_python_unused_detection():
    analyser = PythonAnalyser()
    source = '''
def my_func():
    print('Test')

def foo():
    x = 1
    y = 2  # y unused
    my_func()
    return x

def bar():
    pass
'''
    ast_node = analyser.parse(source)
    unused = analyser.find_unused(ast_node)
    unused_variables = [name for name,_ in unused.unused_variables]
    unused_functions = [name for name,_ in unused.unused_functions]

    assert 'x' not in unused_variables
    assert 'y' in unused_variables
    assert 'foo' in unused_functions
    assert 'bar' in unused_functions
    assert 'my_func' not in unused_functions


def test_python_identifier():
    analyser = PythonAnalyser()
    source = '''
def foo():
    x = 1
    y = 2
    return x + y

class Bar:
    pass
'''
    ast_node = analyser.parse(source)
    identifers = analyser.get_identifiers(ast_node)
    assert identifers.functions == {'foo'}
    assert identifers.classes == {'Bar'}
    assert identifers.variables == {'x', 'y'}


def test_engine_analyse_file(tmp_path: Path):
    source = '''
def foo():
    x = 1
    y = 2
    return x # comment

class Bar:
    pass
'''
    file = tmp_path / 'code.py'
    file.write_text(source)
    engine = AnalyserEngine()
    result = engine.analyse_file(str(file))
    # check identifiers:
    assert result.identifiers.functions == {'foo'}
    assert result.identifiers.variables == {'x', 'y'}
    assert result.identifiers.classes == {'Bar'}
    
    # check comment count:
    assert result.comment_count == 1

    # check unused: 
    assert [name for name,_ in result.unused_report.unused_functions] == ['foo']
    assert [name for name,_ in result.unused_report.unused_variables] == ['y']


def test_python_comment_hash_in_string():
    source = '''
x = "# this is NOT a comment"
# this is a real comment
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 1

def test_python_comment_hash_in_multiline_string():
    source = '''
x = """
# this is NOT a comment"""
# this is a real comment
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 1

def test_python_docstring_only():
    source = '''
"""Module docstring"""
def foo():
    pass
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 1
    
def test_python_multiline_and_docstring():
    source = '''
"""Module docstring"""

"""Multiline 
comment
"""
def foo():
    pass
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 2


def test_python_no_comments():
    source = '''
def foo():
    pass
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 0


def test_python_empty_file():
    source = ""
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    count = analyser.count_comments(ast_node, source)
    assert count == 0

def test_python_complex_integration():
    source = '''
"""Module docstring"""
import os

def main():
    x = 1
    y = 2
    z = 3 # unused
    a,b = 1,2 # multiple assignment on single line
    c,d = (3,4) # tuple unpacking
    e,f = [5,6] # list unpacking

    def inner_function():
        # inner comment
        return x+y
    return inner()

class Foo:
    """Class docstring"""
    value = 42
    def method():
        raise ValueError("Oops")

def unused_function():
    pass

# lonely comment
'''
    analyser = PythonAnalyser()
    ast_node = analyser.parse(source)
    ids = analyser.get_identifiers(ast_node)
    assert set(['main', 'inner_function']).issubset(ids.functions)
    assert set(['Foo']).issubset(ids.classes)
    assert set(['x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f']).issubset(ids.variables) # currently fails
    assert analyser.count_comments(ast_node, source) == 8
    unused = analyser.find_unused(ast_node)
    unused_functions = set([name for name,_ in unused.unused_functions])
    unused_variables = set([name for name,_ in unused.unused_variables])
    assert set(['z', 'a', 'b', 'c', 'd', 'e', 'f']).issubset(unused_variables)
    assert 'unused_function' in unused_functions
