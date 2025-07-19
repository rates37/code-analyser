from code_analyser.languages.java import JavaAnalyser
from code_analyser.utils.brace import BraceConfig


JAVA_SOURCE = '''
// This is a comment
public class HelloWorld {
    public static void main(String[] args) {
        int x = 5;  // variable
        int y = 10;
        int unusedVar = 0;
        foo(x,y);
    }
    // another comment
    public void foo(int a, int b) {
        System.out.println("bar: " + (a+b));
    }
    public void unusedFunc() { 
    }
}
'''


def test_java_identifiers():
    analyser = JavaAnalyser()
    ast = analyser.parse(JAVA_SOURCE)
    ids = analyser.get_identifiers(ast)

    assert set(['main', 'foo', 'unusedFunc']).issubset(ids.functions)
    assert set(['x', 'y', 'unusedVar']).issubset(ids.variables)
    assert 'HelloWorld' in ids.classes


def test_java_comment_count():
    analyser = JavaAnalyser()
    ast = analyser.parse(JAVA_SOURCE)
    count = analyser.count_comments(ast, JAVA_SOURCE)
    assert count == 3


def test_java_comment_count_multiple_in_line():
    source = '''
// first comment // still same comment // 
public class HelloWorld {
    public static void main(String[] args) {
        int x = 5; // variable
    }
}
'''
    analyser = JavaAnalyser()
    ast = analyser.parse(source)
    count = analyser.count_comments(ast, source)
    assert count == 2


def test_java_brace_style_kr():
    analyser = JavaAnalyser()
    report = analyser.check_brace_style(JAVA_SOURCE, BraceConfig('K&R'))
    assert report.violations == []


def test_java_brace_style_allman():
    source = '''
public class HelloWorld
{
    public static void main(String[] args)
    {
        int x = 0;
    }
}
'''
    analyser = JavaAnalyser()
    report = analyser.check_brace_style(source, BraceConfig('Allman'))
    assert report.violations == []


def test_java_brace_style_whitesmith():
    source = '''
public class HelloWorld
    {
        public static void main(String[] args)
            {
                int x = 0;
            }
    }
'''
    analyser = JavaAnalyser()
    report = analyser.check_brace_style(source, BraceConfig('Whitesmith'))
    assert report.violations == []


def test_java_unused_detection():
    analyser = JavaAnalyser()
    ast = analyser.parse(JAVA_SOURCE)
    unused = analyser.find_unused(ast)
    unused_variables = [name for name, _ in unused.unused_variables]
    unused_functions = [name for name, _ in unused.unused_functions]
    assert set(['unusedFunc']).issubset(unused_functions)
    assert set(['unusedVar']).issubset(unused_variables)
    assert 'x' not in unused_variables
    assert 'y' not in unused_variables
    assert 'foo' not in unused_functions

def test_java_comment_count_slash_in_string():
    source = '''
// This is a comment
public class HelloWorld {
    public static void main(String[] args) {
        String s = "Hello // there are slashes in this string";
    }
}
'''
    analyser = JavaAnalyser()
    ast = analyser.parse(source)
    count = analyser.count_comments(ast, source)
    assert count == 1

def test_java_comment_count_multiline_comment_in_string():
    source = '''
// This is a comment
public class HelloWorld {
    public static void main(String[] args) {
        String s = "Hello /* this looks like a multiline comment but its not, it's a string */";
    }
}
'''
    analyser = JavaAnalyser()
    ast = analyser.parse(source)
    count = analyser.count_comments(ast, source)
    assert count == 1