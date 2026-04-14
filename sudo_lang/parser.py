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
import time
from .nodes import KEYWORDS, node
from .lexer import tokenise
from .util import KEYWORD_NOT_FOUND


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

        elif keyword in ("CATCH", "EXCEPT"):
            return None  # handled inside _parse_try

        elif keyword.startswith("END"):
            return None  # block terminators consumed by parse_block

        elif keyword == "REPEAT_UNTIL":
            return self._parse_repeat_until(tokens)

        elif keyword == "REPEAT":
            return self._parse_repeat(tokens, line)

        elif keyword == "FUNCTION":
            return self._parse_function(tokens, line)

        elif keyword == "RETURN":
            return self._parse_return(tokens)
        
        elif keyword == "CLEAR_CONSOLE":
            return self._parse_CLEAR_CONSOLE(tokens, line)
        
        elif keyword == "TRY":
            return self._parse_try(tokens, line)

        elif keyword == "PASS":
            return self._parse_pass(tokens, line)

        elif keyword == "USING":
            return self._parse_using(tokens, line)

        # ---- Expression statement — bare expression on its own line -------
        # If the line isn't a recognised keyword, treat the whole line as an
        # expression that is evaluated at runtime (result discarded).
        # This lets TRY/CATCH capture undefined-variable errors, e.g.:
        #   TRY
        #       ERWREW          <- runtime error, caught by CATCH
        #   CATCH
        #       DISPLAY error
        #   END TRY
        else:
            return node("EXPR", expr=line)

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

        Use this with list item assignment to avoid ambiguity with the shorthand form:
        SET mylist[0] <- 5   (valid)
        mylist[0] <- 5     (valid)

        """
        #check is it list assignment?
        list_assign = re.match(r'^(\w+\[.*\])\s*<-.*$', line)
        if list_assign:
            #get the list name and index
            varname = list_assign.group(1)
            #create a display node for debugging
            node("DISPLAY", expr=f"Parsing list assignment to {varname}")
            expr = line.split("<-", 1)[1].strip() # everything after the first <- is the expression
            #instead of creating a SET node, we create a special node for list assignment
            return node("LIST_SET", var=varname, expr=expr)
        


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
        INPUT(prompt) - returns a value to store in varname
        Reads a value from the user and stores it in varname.
        """
        # Try parenthesised form first: INPUT(...) or INPUT (...)
        paren_match = re.match(r'^INPUT\s*\((\w+)\)\s*$', line, re.IGNORECASE)
        if paren_match:
            varname = paren_match.group(1)
            prompt = prompt = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return node("INPUT", var=varname, prompt=prompt)

        else:
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

    def _parse_CLEAR_CONSOLE(self, tokens, line):
        """
        CLEAR_CONSOLE

        Clears the console output. No arguments.
        """
        return node("CLEAR_CONSOLE")

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

    def _parse_repeat_until(self, tokens):
        """
        REPEAT_UNTIL condition
            ...
        END REPEAT_UNTIL

        DO is optional.
        """
        upper = [t.upper() for t in tokens]
        condition = " ".join(tokens[1:])

        body, _ = self.parse_block({"END"})
        if not self._at_end():
            self._consume()  # consume END REPEAT_UNTIL

        return node("WHILE", condition=condition, body=body)

    def _parse_repeat(self, tokens, line):
        """
        REPEAT n TIMES
            ...
        END REPEAT
        """
        upper = [t.upper() for t in tokens]
        if "TIMES" not in upper:
            raise ParseError(f"REPEAT requires 'TIMES': {line}")
        times_idx = upper.index("TIMES")
        if times_idx < 2:
            raise ParseError(f"REPEAT missing iteration count: {line}")
        count_expr = " ".join(tokens[1:times_idx])
        varname = f"_i{self.pos}"  # unique loop variable name based on current line number
        start_expr = "0"
        end_expr = count_expr
        body, _ = self.parse_block({"END"})
        if not self._at_end():
            self._consume()  # consume END REPEAT   

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
<<<<<<< HEAD

    def _parse_try(self, tokens, line):
        """
        TRY
            ...
        CATCH
            ...
        END TRY

        CATCH is optional.
        """
        # Accept CATCH or EXCEPT as the handler opener; END / ENDTRY as the closer
        try_body, terminator = self.parse_block({"CATCH", "EXCEPT", "END", "ENDTRY"})

        catch_body = []
        error_var = None
        if terminator in ("CATCH", "EXCEPT"):
            catch_tokens = tokenise(self._consume())
            # Default error variable is always "error"; a custom name can follow CATCH
            error_var = catch_tokens[1] if len(catch_tokens) > 1 else "error"
            catch_body, _ = self.parse_block({"END", "ENDTRY"})

        if not self._at_end():
            self._consume()  # consume END TRY / ENDTRY

        return node("TRY", try_body=try_body, catch_body=catch_body, error_var=error_var)

    def _parse_pass(self, tokens, line):
        """
        PASS

        Does nothing. Useful as a placeholder in empty blocks.
        """
        return node("PASS")

    def _parse_using(self, tokens, line):
        """
        USING filename

        Imports and executes another .sudo file in the current scope.
        The filename is taken as-is (quotes are stripped if present).
        If no extension is given, .sudo is appended automatically.
        """
        if len(tokens) < 2:
            raise ParseError("USING requires a filename: USING myfile")
        filename = tokens[1].strip('"').strip("'")
        if not filename.endswith(".sudo"):
            filename += ".sudo"
        return node("USING", filename=filename)
=======
>>>>>>> a7852da16b35f3afc327267c4906d96bc3ec42fd
