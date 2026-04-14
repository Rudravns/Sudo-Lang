<<<<<<< HEAD
=======
<<<<<<< HEAD
"""
nodes.py — keyword registry and AST node factory.

KEYWORDS
--------
The set of all recognised keywords.  Add new keywords here when extending
the language — this is the single source of truth used by the parser,
interpreter, and any tooling (syntax highlighters, linters, etc.).

node()
------
A lightweight helper that creates an AST node as a plain dict.  Each node
has at minimum a "type" key; all other fields are keyword-specific.

Example node shapes:
    {"type": "SET",      "var": "x",    "expr": "5"}
    {"type": "DISPLAY",  "expr": "x"}
    {"type": "IF",       "condition": "x > 0", "true_body": [...], "false_body": [...]}
    {"type": "WHILE",    "condition": "x < 10", "body": [...]}
    {"type": "FOR",      "var": "i", "start": "1", "end": "5", "body": [...]}
    {"type": "FUNCTION", "name": "greet", "params": ["name"], "body": [...]}
    {"type": "RETURN",   "expr": "value"}
    {"type": "INPUT",    "var": "x", "prompt": ""}
"""

# ---------------------------------------------------------------------------
# Add new keywords here when expanding the language
# ---------------------------------------------------------------------------
KEYWORDS = {
    "SET",
    "INPUT",
    "DISPLAY",
    "IF",
    "ELSE",
    "WHILE",
    "FOR",
    "FUNCTION",
    "RETURN",
    "CLEAR_CONSOLE",
    "TRY",
    "CATCH",
    "PASS",


    # NEW KEYWORDS GO HERE — also update parser.py and interpreter.py
}


def node(node_type, **kwargs):
    """Create and return an AST node dict with the given type and fields."""
    return {"type": node_type, **kwargs}
=======
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd
"""
nodes.py — keyword registry and AST node factory.

KEYWORDS
--------
The set of all recognised keywords.  Add new keywords here when extending
the language — this is the single source of truth used by the parser,
interpreter, and any tooling (syntax highlighters, linters, etc.).

node()
------
A lightweight helper that creates an AST node as a plain dict.  Each node
has at minimum a "type" key; all other fields are keyword-specific.

Example node shapes:
    {"type": "SET",      "var": "x",    "expr": "5"}
    {"type": "DISPLAY",  "expr": "x"}
    {"type": "IF",       "condition": "x > 0", "true_body": [...], "false_body": [...]}
    {"type": "WHILE",    "condition": "x < 10", "body": [...]}
<<<<<<< HEAD
    {"type": "REPEAT",   "condition": "x < 10", "body": [...]}
=======
    {"type": "FOR",      "var": "i", "start": "1", "end": "5", "body": [...]}
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd
    {"type": "FUNCTION", "name": "greet", "params": ["name"], "body": [...]}
    {"type": "RETURN",   "expr": "value"}
    {"type": "INPUT",    "var": "x", "prompt": ""}
"""

# ---------------------------------------------------------------------------
# Add new keywords here when expanding the language
# ---------------------------------------------------------------------------
KEYWORDS = {
    "SET",
    "INPUT",
    "DISPLAY",
    "IF",
    "ELSE",
<<<<<<< HEAD
    "REPEAT_UNTIL",  # "REPEAT ... UNTIL" loop, condition at end of block
    "REPEAT",
=======
    "WHILE",
    "FOR",
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd
    "FUNCTION",
    "RETURN",
    "CLEAR_CONSOLE",
    "TRY",
    "CATCH",
    "PASS",

<<<<<<< HEAD
    # Aliases — accepted as alternatives to the canonical keyword above
    "EXCEPT",  # alias for CATCH

    # File import
    "USING",
=======
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd

    # NEW KEYWORDS GO HERE — also update parser.py and interpreter.py
}


def node(node_type, **kwargs):
    """Create and return an AST node dict with the given type and fields."""
    return {"type": node_type, **kwargs}
<<<<<<< HEAD
=======
>>>>>>> 6b57c60b73b91e74482c9e44f1a09859fb26185e
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd
