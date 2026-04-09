"""
sudo_interpreter.py
-------------------
Interpreter for the "sudo code" language (.sudo files).

Supported keywords (base set):
  SET       - variable assignment:   SET x <- 5
  INPUT     - read user input:       INPUT x
  DISPLAY   - print to console:      DISPLAY x  or  DISPLAY "hello"
  IF        - conditional block:     IF condition THEN ... END IF
  ELSE      - else branch:           ELSE ... END IF
  WHILE     - while loop:            WHILE condition DO ... END WHILE
  FOR       - for loop:              FOR x FROM 1 TO 5 ... END FOR
  FUNCTION  - define a function:     FUNCTION name(params) ... END FUNCTION
  RETURN    - return a value:        RETURN value

Unrecognized keywords are silently ignored so the language can be expanded.

To add new keywords:
  1. Add the keyword to KEYWORDS below (for documentation/syntax highlighting).
  2. Add a parsing branch in Parser.parse_line() or Parser.parse_block().
  3. Add an evaluation branch in Interpreter.execute().
"""

import sys
import re

# ---------------------------------------------------------------------------
# KEYWORDS — extend this list when adding new keywords
# ---------------------------------------------------------------------------
KEYWORDS = {
    "SET", "INPUT", "DISPLAY",
    "IF", "ELSE", "WHILE", "FOR",
    "FUNCTION", "RETURN",
    # Add new keywords here:
}

# ---------------------------------------------------------------------------
# AST NODE TYPES
# Each node is a plain dict with a "type" key plus type-specific fields.
# ---------------------------------------------------------------------------

def node(node_type, **kwargs):
    """Helper to create an AST node dict."""
    return {"type": node_type, **kwargs}


# ---------------------------------------------------------------------------
# LEXER — tokenises a single line into a list of string tokens
# ---------------------------------------------------------------------------

def tokenise(line):
    """Split a line into tokens, respecting quoted strings."""
    tokens = []
    # Match quoted strings or non-whitespace sequences
    for match in re.finditer(r'"[^"]*"|\'[^\']*\'|\S+', line):
        tokens.append(match.group())
    return tokens


# ---------------------------------------------------------------------------
# PARSER
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass


class Parser:
    """
    Parses a list of lines into an AST (list of node dicts).

    The parser works recursively: parse_block() reads lines until it hits
    an END keyword (END IF, END WHILE, etc.), then returns the collected
    nodes.  This makes it easy to nest blocks.
    """

    def __init__(self, lines):
        # Strip comments (lines starting with #) and blank lines, keep index
        self.lines = []
        for raw in lines:
            stripped = raw.strip()
            if stripped and not stripped.startswith("#"):
                self.lines.append(stripped)
        self.pos = 0  # current line index

    def at_end(self):
        return self.pos >= len(self.lines)

    def peek(self):
        if self.at_end():
            return None
        return self.lines[self.pos]

    def consume(self):
        line = self.lines[self.pos]
        self.pos += 1
        return line

    # ------------------------------------------------------------------ #
    # Top-level parse — returns a list of AST nodes                       #
    # ------------------------------------------------------------------ #

    def parse(self):
        nodes = []
        while not self.at_end():
            n = self.parse_statement()
            if n is not None:
                nodes.append(n)
        return nodes

    def parse_block(self, end_keywords):
        """
        Parse lines until a line whose first token matches any of
        end_keywords.  Returns (body_nodes, terminator_token).

        To add a new block keyword, add its END marker to end_keywords
        in the caller and handle the body here.
        """
        body = []
        while not self.at_end():
            line = self.peek()
            tokens = tokenise(line)
            if tokens and tokens[0].upper() in end_keywords:
                return body, tokens[0].upper()
            n = self.parse_statement()
            if n is not None:
                body.append(n)
        raise ParseError(f"Unexpected end of file; expected one of: {end_keywords}")

    # ------------------------------------------------------------------ #
    # Statement dispatch                                                   #
    # ------------------------------------------------------------------ #

    def parse_statement(self):
        """Parse one statement from the current line and return an AST node."""
        line = self.consume()
        tokens = tokenise(line)
        if not tokens:
            return None

        keyword = tokens[0].upper()

        # ---- Implicit assignment: varname <- expr  (without SET) -------
        # Supports: a <- 6  or  a <- b + c
        if "<-" in tokens and keyword not in KEYWORDS:
            return self._parse_implicit_assignment(tokens, line)

        # ---- SET -------------------------------------------------------
        if keyword == "SET":
            # SET x <- expression
            return self._parse_set(tokens, line)

        # ---- INPUT -----------------------------------------------------
        elif keyword == "INPUT":
            # INPUT varname
            return self._parse_input(tokens)

        # ---- DISPLAY ---------------------------------------------------
        # Supports both:  DISPLAY expr   and   DISPLAY(expr)
        elif keyword == "DISPLAY" or re.match(r'^DISPLAY\s*\(', line, re.IGNORECASE):
            return self._parse_display(tokens, line)

        # ---- IF --------------------------------------------------------
        elif keyword == "IF":
            # IF condition THEN
            return self._parse_if(tokens, line)

        # ---- ELSE handled inside _parse_if ----------------------------
        elif keyword == "ELSE":
            # Should not appear at top level; treat as unknown
            return None

        # ---- END (end of block marker) --------------------------------
        elif keyword.startswith("END"):
            # Consumed by parse_block; if reached here, ignore
            return None

        # ---- WHILE -----------------------------------------------------
        elif keyword == "WHILE":
            # WHILE condition DO
            return self._parse_while(tokens, line)

        # ---- FOR -------------------------------------------------------
        elif keyword == "FOR":
            # FOR x FROM start TO end
            return self._parse_for(tokens)

        # ---- FUNCTION --------------------------------------------------
        elif keyword == "FUNCTION":
            # FUNCTION name(params)
            return self._parse_function(tokens, line)

        # ---- RETURN ----------------------------------------------------
        elif keyword == "RETURN":
            # RETURN expression
            return self._parse_return(tokens, line)

        # ---- UNKNOWN keyword — ignore (allows future expansion) --------
        else:
            return None

    # ------------------------------------------------------------------ #
    # Individual statement parsers                                         #
    # ------------------------------------------------------------------ #

    def _parse_implicit_assignment(self, tokens, line):
        """varname <- expression  (shorthand assignment without SET)"""
        try:
            arrow_idx = tokens.index("<-")
        except ValueError:
            raise ParseError(f"Assignment missing '<-': {line}")
        varname = tokens[0]
        expr_tokens = tokens[arrow_idx + 1:]
        expr = " ".join(expr_tokens)
        return node("SET", var=varname, expr=expr)

    def _parse_set(self, tokens, line):
        """SET varname <- expression"""
        # Find the <- operator
        try:
            arrow_idx = tokens.index("<-")
        except ValueError:
            raise ParseError(f"SET statement missing '<-': {line}")
        if arrow_idx < 2:
            raise ParseError(f"SET statement missing variable name: {line}")
        varname = tokens[1]
        expr_tokens = tokens[arrow_idx + 1:]
        expr = " ".join(expr_tokens)
        return node("SET", var=varname, expr=expr)

    def _parse_input(self, tokens):
        """INPUT varname"""
        if len(tokens) < 2:
            raise ParseError("INPUT statement missing variable name")
        varname = tokens[1]
        # Optional prompt string as remaining tokens
        prompt = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        return node("INPUT", var=varname, prompt=prompt)

    def _parse_display(self, tokens, line):
        """DISPLAY expression  —  also handles  DISPLAY(expression)"""
        # Check for parenthesised form: DISPLAY(expr) or DISPLAY (expr)
        paren_match = re.match(r'^DISPLAY\s*\((.+)\)\s*$', line, re.IGNORECASE)
        if paren_match:
            expr = paren_match.group(1).strip()
        else:
            # Plain form: DISPLAY expr
            expr = " ".join(tokens[1:])
        return node("DISPLAY", expr=expr)

    def _parse_if(self, tokens, line):
        """IF condition THEN ... [ELSE ...] END IF"""
        # Condition is everything between IF and THEN
        try:
            then_idx = [t.upper() for t in tokens].index("THEN")
        except ValueError:
            # THEN is optional — treat rest as condition
            then_idx = len(tokens)
        condition = " ".join(tokens[1:then_idx])

        # Parse the true branch until ELSE or END
        true_body, terminator = self.parse_block({"ELSE", "END"})

        false_body = []
        if terminator == "ELSE":
            self.consume()  # consume the ELSE line
            false_body, _ = self.parse_block({"END"})

        # Consume "END IF" line
        if not self.at_end():
            self.consume()

        return node("IF", condition=condition, true_body=true_body, false_body=false_body)

    def _parse_while(self, tokens, line):
        """WHILE condition DO ... END WHILE"""
        # Condition is everything between WHILE and DO
        upper = [t.upper() for t in tokens]
        try:
            do_idx = upper.index("DO")
        except ValueError:
            do_idx = len(tokens)
        condition = " ".join(tokens[1:do_idx])

        body, _ = self.parse_block({"END"})
        if not self.at_end():
            self.consume()  # consume END WHILE

        return node("WHILE", condition=condition, body=body)

    def _parse_for(self, tokens):
        """FOR varname FROM start TO end ... END FOR"""
        # Expected: FOR x FROM 1 TO 10
        upper = [t.upper() for t in tokens]
        try:
            from_idx = upper.index("FROM")
            to_idx = upper.index("TO")
        except ValueError:
            raise ParseError(f"FOR statement malformed: {' '.join(tokens)}")

        varname = tokens[1]
        start_expr = " ".join(tokens[from_idx + 1:to_idx])
        end_expr = " ".join(tokens[to_idx + 1:])

        body, _ = self.parse_block({"END"})
        if not self.at_end():
            self.consume()  # consume END FOR

        return node("FOR", var=varname, start=start_expr, end=end_expr, body=body)

    def _parse_function(self, tokens, line):
        """FUNCTION name(param1, param2, ...) ... END FUNCTION"""
        # Reconstruct the declaration to extract name and params
        declaration = " ".join(tokens[1:])
        match = re.match(r'(\w+)\s*\(([^)]*)\)', declaration)
        if not match:
            raise ParseError(f"FUNCTION declaration malformed: {line}")
        name = match.group(1)
        raw_params = match.group(2)
        params = [p.strip() for p in raw_params.split(",") if p.strip()]

        body, _ = self.parse_block({"END"})
        if not self.at_end():
            self.consume()  # consume END FUNCTION

        return node("FUNCTION", name=name, params=params, body=body)

    def _parse_return(self, tokens, line):
        """RETURN expression"""
        expr = " ".join(tokens[1:])
        return node("RETURN", expr=expr)


# ---------------------------------------------------------------------------
# INTERPRETER
# ---------------------------------------------------------------------------

class ReturnSignal(Exception):
    """Used to propagate RETURN values up the call stack."""
    def __init__(self, value):
        self.value = value


class Interpreter:
    """
    Walks the AST and executes each node.

    Environment: variables live in a plain dict (scope).
    Functions are stored in self.functions and looked up by name.

    To add a new statement type:
      1. Parse it in Parser.parse_statement() → a new node type dict.
      2. Add an elif branch in self.execute() that handles that node type.
    """

    def __init__(self):
        self.global_scope = {}   # global variable namespace
        self.functions = {}      # name -> node("FUNCTION", ...)

    # ------------------------------------------------------------------ #
    # Public entry point                                                   #
    # ------------------------------------------------------------------ #

    def run(self, ast, scope=None):
        """Execute a list of AST nodes in the given scope (defaults to global)."""
        if scope is None:
            scope = self.global_scope
        for n in ast:
            self.execute(n, scope)

    # ------------------------------------------------------------------ #
    # Statement execution                                                  #
    # ------------------------------------------------------------------ #

    def execute(self, n, scope):
        """Dispatch on node type and execute."""
        t = n["type"]

        # ---- SET -------------------------------------------------------
        if t == "SET":
            scope[n["var"]] = self.eval_expr(n["expr"], scope)

        # ---- INPUT -----------------------------------------------------
        elif t == "INPUT":
            prompt = self.eval_expr(n["prompt"], scope) if n["prompt"] else ""
            try:
                value = input(str(prompt) + " " if prompt else "")
            except EOFError:
                value = ""
            # Try to coerce to number; keep string otherwise
            scope[n["var"]] = self._coerce(value)

        # ---- DISPLAY ---------------------------------------------------
        elif t == "DISPLAY":
            result = self.eval_expr(n["expr"], scope)
            print(result)

        # ---- IF --------------------------------------------------------
        elif t == "IF":
            condition = self.eval_expr(n["condition"], scope)
            if condition:
                self.run(n["true_body"], scope)
            else:
                self.run(n["false_body"], scope)

        # ---- WHILE -----------------------------------------------------
        elif t == "WHILE":
            while self.eval_expr(n["condition"], scope):
                self.run(n["body"], scope)

        # ---- FOR -------------------------------------------------------
        elif t == "FOR":
            start = int(self.eval_expr(n["start"], scope))
            end = int(self.eval_expr(n["end"], scope))
            for i in range(start, end + 1):
                scope[n["var"]] = i
                self.run(n["body"], scope)

        # ---- FUNCTION (definition, not call) ---------------------------
        elif t == "FUNCTION":
            self.functions[n["name"]] = n

        # ---- RETURN ----------------------------------------------------
        elif t == "RETURN":
            value = self.eval_expr(n["expr"], scope) if n["expr"] else None
            raise ReturnSignal(value)

        # ---- Unknown node type — ignore (allows future expansion) ------
        else:
            pass

    # ------------------------------------------------------------------ #
    # Expression evaluator                                                 #
    # ------------------------------------------------------------------ #

    def eval_expr(self, expr, scope):
        """
        Evaluate a sudo-code expression string and return the Python value.

        Handles:
          - Quoted string literals: "hello"
          - Numeric literals: 42, 3.14
          - Variable references: x
          - Function calls: name(arg1, arg2)
          - Arithmetic/comparison via Python's eval()

        To add new expression forms, extend this method.
        """
        expr = expr.strip()

        if not expr:
            return None

        # Quoted string literal
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Function call: name(args)
        func_match = re.match(r'^(\w+)\(([^)]*)\)$', expr)
        if func_match:
            fname = func_match.group(1)
            raw_args = func_match.group(2)
            args = [self.eval_expr(a.strip(), scope) for a in raw_args.split(",") if a.strip() != ""]
            return self._call_function(fname, args, scope)

        # Substitute variables then evaluate with Python
        return self._eval_python_expr(expr, scope)

    def _eval_python_expr(self, expr, scope):
        """
        Substitute sudo-code variables and operators into a Python expression
        and evaluate it safely.
        """
        # Replace sudo-code string operators with Python equivalents
        expr = re.sub(r'\bAND\b', 'and', expr)
        expr = re.sub(r'\bOR\b', 'or', expr)
        expr = re.sub(r'\bNOT\b', 'not', expr)
        expr = re.sub(r'\bMOD\b', '%', expr)

        # Build a safe evaluation context from the current scope
        safe_env = {}
        safe_env.update(scope)
        # Expose basic builtins that are useful in expressions
        safe_env.update({
            "True": True, "False": False, "None": None,
            "abs": abs, "len": len, "str": str,
            "int": int, "float": float, "round": round,
        })

        try:
            return eval(expr, {"__builtins__": {}}, safe_env)
        except Exception:
            # If eval fails, return the expression as a string (best-effort)
            return expr

    def _call_function(self, name, args, caller_scope):
        """Call a user-defined FUNCTION by name with evaluated args."""
        if name not in self.functions:
            raise NameError(f"Undefined function: '{name}'")
        func_node = self.functions[name]
        # Create a fresh local scope, pre-populate with parameters
        local_scope = {}
        for i, param in enumerate(func_node["params"]):
            local_scope[param] = args[i] if i < len(args) else None
        try:
            self.run(func_node["body"], local_scope)
        except ReturnSignal as ret:
            return ret.value
        return None

    def _coerce(self, value):
        """Try to convert a string to int or float; otherwise keep as str."""
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value


# ---------------------------------------------------------------------------
# MAIN — read a .sudo file and run it
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python sudo_interpreter.py <file.sudo>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not filepath.endswith(".sudo"):
        print(f"Warning: '{filepath}' does not have a .sudo extension.")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found: '{filepath}'")
        sys.exit(1)

    # Parse
    try:
        parser = Parser(source)
        ast = parser.parse()
    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    # Execute
    interpreter = Interpreter()
    try:
        interpreter.run(ast)
    except ReturnSignal:
        pass  # RETURN at top level — ignore
    except Exception as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
