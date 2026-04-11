"""
sudo_lang — the sudo code language package.

Public API:
    run_file(filepath)   — parse and execute a .sudo source file
    run_source(source)   — parse and execute a string of sudo code

Package layout:
    nodes.py        — KEYWORDS set and node() helper
    lexer.py        — tokenise() function
    parser.py       — Parser class, ParseError
    interpreter.py  — Interpreter class, ReturnSignal
"""

from .nodes import KEYWORDS, node
from .lexer import tokenise
from .parser import Parser, ParseError
from .interpreter import Interpreter, ReturnSignal


def run_file(filepath):
    """Read a .sudo file and execute it. Raises on parse/runtime errors."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.readlines()
    _execute(source)


def run_source(source):
    """Execute a string (or list of lines) of sudo code directly."""
    if isinstance(source, str):
        source = source.splitlines(keepends=True)
    _execute(source)


def _execute(lines):
    parser = Parser(lines)
    ast = parser.parse()
    interpreter = Interpreter()
    try:
        interpreter.run(ast)
    except ReturnSignal:
        pass
