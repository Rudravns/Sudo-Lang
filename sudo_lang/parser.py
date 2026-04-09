"""
parser.py — recursive-descent parser for the sudo code language.

Public classes:
    ParseError   — raised on malformed input
    Parser       — converts source lines into an AST (list of node dicts)

How to add a new statement keyword:
    1. Add it to KEYWORDS in nodes.py.
    2. Add an elif branch in Parser.parse_statement() that calls a new
       _parse_<keyword>() method.
    3. If the keyword opens a block (like IF, WHILE), use parse_block()
       and provide an appropriate set of end-markers.

How blocks work:
    parse_block(end_keywords) reads statements until it sees a line whose
    first token is in end_keywords, then returns the collected body and the
    terminator token.  This enables arbitrarily nested blocks.
"""

import re
from .nodes import KEYWORDS, node
from .lexer import tokenise


class ParseError(Exception):
    """Raised when the parser encounters invalid sudo code syntax."""


class Parser:
    """
    Parses a list of source lines into an AST.

    Usage:
        parser = Parser(lines)
        ast    = parser.parse()   # list of node dicts
    """

    def __init__(self, lines):
        # Remove blank lines and strip comments before storing lines.
        # Supported comment styles:
        #   #  ...   (hash — full line or inline)
        #   // ...   (double-slash — full line or inline)
        cleaned = []
        for raw in lines:
            line = self._strip_comment(raw.strip())
            if line:
                cleaned.append(line)
        self.lines = cleaned
        self.pos = 0

    @staticmethod
    def _strip_comment(line):
        """
        Remove any trailing comment from a line and return the code part.
        Handles both # and // comment styles.
        Quoted strings are respected — a # or // inside quotes is NOT a comment.
        """
        result = []
        in_string = None  # tracks the opening quote character (" or ')
        i = 0
        while i < len(line):
            ch = line[i]
            if in_string:
                result.append(ch)
                if ch == in_string:
                    in_string = None  # closing quote
            else:
                if ch in ('"', "'"):
                    in_string = ch
                    result.append(ch)
                elif ch == '#':
                    break  # rest of line is a comment
                elif ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    break  # rest of line is a // comment
                else:
                    result.append(ch)
            i += 1
        return "".join(result).strip()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _at_end(self):
        return self.pos >= len(self.lines)

    def _peek(self):
        return self.lines[self.pos] if not self._at_end() else None

    def _consume(self):
        line = self.lines[self.pos]
        self.pos += 1
        return line

    # ------------------------------------------------------------------ #
    # Top-level entry point                                                #
    # ------------------------------------------------------------------ #

    def parse(self):
        """Parse all lines and return a list of AST nodes."""
        nodes = []
        while not self._at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                nodes.append(stmt)
        return nodes

    def parse_block(self, end_keywords):
        """
        Parse statements until a line starting with one of end_keywords.

        Returns (body, terminator) where body is a list of AST nodes and
        terminator is the end keyword that was found (e.g. "END", "ELSE").

        To add a new block construct, define its end markers here and call
        parse_block() from the corresponding _parse_<keyword>() method.
        """
        body = []
        while not self._at_end():
            tokens = tokenise(self._peek())
            if tokens and tokens[0].upper() in end_keywords:
                return body, tokens[0].upper()
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        raise ParseError(
            f"Reached end of file while looking for: {end_keywords}"
        )

    # ------------------------------------------------------------------ #
    # Statement dispatch                                                   #
    # ------------------------------------------------------------------ #

    def parse_statement(self):
        """Read one line and return the corresponding AST node (or None)."""
        line = self._consume()
        tokens = tokenise(line)
        if not tokens:
            return None

        # Extract the keyword from the first token — case-insensitive.
        # Handles both  DISPLAY expr  and  DISPLAY(expr)  (parens attached).
        raw_first = tokens[0]
        # Strip any trailing parenthesis/arguments to get just the keyword
        keyword = re.split(r'[\s(]', raw_first)[0].upper()

        # ---- Shorthand assignment: varname <- expr  (SET is optional) --
        # Supports both:  SET x <- 5   and   x <- 5
        if "<-" in tokens and keyword not in KEYWORDS:
            return self._parse_assignment(tokens, line)

        if keyword == "SET":
            return self._parse_set(tokens, line)

        elif keyword == "INPUT":
            return self._parse_input(tokens, line)

        elif keyword == "DISPLAY":
            # Supports:  DISPLAY expr       (space-separated)
            #            DISPLAY(expr)      (parens, no space)
            #            DISPLAY (expr)     (parens, with space)
            return self._parse_display(tokens, line)

        elif keyword == "IF":
            return self._parse_if(tokens)

        elif keyword == "ELSE":
            return None  # handled inside _parse_if

        elif keyword.startswith("END"):
            return None  # block terminators consumed by parse_block

        elif keyword == "WHILE":
            return self._parse_while(tokens)

        elif keyword == "FOR":
            return self._parse_for(tokens, line)

        elif keyword == "FUNCTION":
            return self._parse_function(tokens, line)

        elif keyword == "RETURN":
            return self._parse_return(tokens)

        # ---- Unknown / future keyword — silently skip ------------------
        # Remove this branch when you want strict mode (error on unknown).
        else:
            return None

    # ------------------------------------------------------------------ #
    # Individual statement parsers                                         #
    # Add a new _parse_<keyword>() method for each new keyword.           #
    # ------------------------------------------------------------------ #

    def _parse_assignment(self, tokens, line):
        """
        varname <- expression   (shorthand — SET keyword is optional)

        Both styles are equivalent:
            SET x <- 5
                x <- 5
        """
        arrow = tokens.index("<-")
        varname = tokens[0]
        expr = " ".join(tokens[arrow + 1:])
        return node("SET", var=varname, expr=expr)

    def _parse_set(self, tokens, line):
        """
        SET varname <- expression

        The <- operator is required.  Everything after <- is the expression.
        """
        if "<-" not in tokens:
            raise ParseError(f"SET requires '<-' operator: {line}")
        arrow = tokens.index("<-")
        if arrow < 2:
            raise ParseError(f"SET missing variable name: {line}")
        varname = tokens[1]
        expr = " ".join(tokens[arrow + 1:])
        return node("SET", var=varname, expr=expr)

    def _parse_input(self, tokens, line):
        """
        INPUT varname
        INPUT varname "optional prompt"

        Reads a value from the user and stores it in varname.
        """
        if len(tokens) < 2:
            raise ParseError(f"INPUT requires a variable name: {line}")
        varname = tokens[1]
        prompt = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        return node("INPUT", var=varname, prompt=prompt)

    def _parse_display(self, tokens, line):
        """
        DISPLAY expression          — space-separated form
        DISPLAY(expression)         — parenthesised form (with or without space)

        Prints the value of expression to the console.
        """
        # Try parenthesised form first: DISPLAY(...) or DISPLAY (...)
        paren_match = re.match(r'^DISPLAY\s*\((.+)\)\s*$', line, re.IGNORECASE)
        if paren_match:
            expr = paren_match.group(1).strip()
        else:
            # Plain form: DISPLAY expr  (everything after the keyword)
            expr = " ".join(tokens[1:])
        return node("DISPLAY", expr=expr)

    def _parse_if(self, tokens):
        """
        IF condition THEN
            ...
        ELSE
            ...
        END IF

        THEN and ELSE are optional.
        """
        upper = [t.upper() for t in tokens]
        then_idx = upper.index("THEN") if "THEN" in upper else len(tokens)
        condition = " ".join(tokens[1:then_idx])

        true_body, terminator = self.parse_block({"ELSE", "END"})

        false_body = []
        if terminator == "ELSE":
            self._consume()  # consume the ELSE line
            false_body, _ = self.parse_block({"END"})

        if not self._at_end():
            self._consume()  # consume END IF

        return node("IF", condition=condition, true_body=true_body, false_body=false_body)

    def _parse_while(self, tokens):
        """
        WHILE condition DO
            ...
        END WHILE

        DO is optional.
        """
        upper = [t.upper() for t in tokens]
        do_idx = upper.index("DO") if "DO" in upper else len(tokens)
        condition = " ".join(tokens[1:do_idx])

        body, _ = self.parse_block({"END"})
        if not self._at_end():
            self._consume()  # consume END WHILE

        return node("WHILE", condition=condition, body=body)

    def _parse_for(self, tokens, line):
        """
        FOR varname FROM start TO end
            ...
        END FOR
        """
        upper = [t.upper() for t in tokens]
        if "FROM" not in upper or "TO" not in upper:
            raise ParseError(f"FOR requires FROM and TO: {line}")
        from_idx = upper.index("FROM")
        to_idx = upper.index("TO")
        varname = tokens[1]
        start_expr = " ".join(tokens[from_idx + 1:to_idx])
        end_expr = " ".join(tokens[to_idx + 1:])

        body, _ = self.parse_block({"END"})
        if not self._at_end():
            self._consume()  # consume END FOR

        return node("FOR", var=varname, start=start_expr, end=end_expr, body=body)

    def _parse_function(self, tokens, line):
        """
        FUNCTION name(param1, param2)
            ...
        END FUNCTION
        """
        declaration = " ".join(tokens[1:])
        match = re.match(r'(\w+)\s*\(([^)]*)\)', declaration)
        if not match:
            raise ParseError(f"FUNCTION declaration malformed: {line}")
        name = match.group(1)
        params = [p.strip() for p in match.group(2).split(",") if p.strip()]

        body, _ = self.parse_block({"END"})
        if not self._at_end():
            self._consume()  # consume END FUNCTION

        return node("FUNCTION", name=name, params=params, body=body)

    def _parse_return(self, tokens):
        """
        RETURN expression

        Returns a value from within a FUNCTION body.
        """
        expr = " ".join(tokens[1:])
        return node("RETURN", expr=expr)
