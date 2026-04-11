"""
lexer.py — tokeniser for the sudo code language.

tokenise(line)
--------------
Splits a single source line into a list of string tokens.

Rules:
  - Quoted strings ("..." or '...') are kept as one token, including spaces.
  - Two-character operators (<-, <=, >=, ==, !=) are split out even without spaces.
  - Single-character operators (<, >, =, !) are split out too.
  - Everything else (identifiers, numbers, parens, commas...) is a token.
  - Comments should be stripped by the caller before tokenising.

Examples:
    tokenise('SET x <- 5')             -> ['SET', 'x', '<-', '5']
    tokenise('aple<-64')               -> ['aple', '<-', '64']
    tokenise('DISPLAY "hello world"')  -> ['DISPLAY', '"hello world"']
    tokenise('IF x >= 0 THEN')         -> ['IF', 'x', '>=', '0', 'THEN']
"""

import re

# Token order matters: longer / more-specific patterns must come first so that
# e.g. '<-' is consumed before a lone '<' could match.
#
#   "..."  or '...' — quoted strings (spaces allowed inside)
#   <=  >=  <-  ==  !=  — two-character operators
#   <  >  =  !          — single-character operators
#   [^\s<>=!]+          — identifiers, numbers, parens, commas, etc.
_TOKEN_PATTERN = re.compile(
    r'"[^"]*"|\'[^\']*\'|<=|>=|<-|==|!=|<|>|[^\s<>=!]+'
)


def tokenise(line):
    """Return a list of string tokens for one source line."""
    return _TOKEN_PATTERN.findall(line)


if __name__ == "__main__":
    for sample in [
        'SET x <- 5',
        'aple<-64',
        'DISPLAY "hello world"',
        'IF x >= 0 THEN',
        'WHILE count != 0 DO',
    ]:
        print(f"{sample!r:40s} -> {tokenise(sample)}")
