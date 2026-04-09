"""
lexer.py — tokeniser for the sudo code language.

tokenise(line)
--------------
Splits a single source line into a list of string tokens.

Rules:
  - Quoted strings ("..." or '...') are kept as one token, including spaces.
  - Everything else is split on whitespace.
  - Comments (# ...) should be stripped by the caller before tokenising.

Examples:
    tokenise('SET x <- 5')           → ['SET', 'x', '<-', '5']
    tokenise('DISPLAY "hello world"') → ['DISPLAY', '"hello world"']
    tokenise('IF x > 0 THEN')        → ['IF', 'x', '>', '0', 'THEN']

To extend the lexer (e.g. multi-character operators, string escapes):
  Update the regex pattern in tokenise() below.
"""

import re

# Matches: double-quoted strings | single-quoted strings | non-whitespace runs
_TOKEN_PATTERN = re.compile(r'"[^"]*"|\'[^\']*\'|\S+')


def tokenise(line):
    """Return a list of tokens from a single source line."""
    return _TOKEN_PATTERN.findall(line)
