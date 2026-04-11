"""
interpreter.py — AST walker and runtime for the sudo code language.

Public classes:
    ReturnSignal   — exception used to propagate RETURN values up the call stack
    Interpreter    — executes a list of AST nodes produced by Parser

How to add a new statement type:
    1. Make sure it is parsed into a node dict in parser.py.
    2. Add an elif branch in Interpreter.execute() for the new node type.

How to add a new expression feature (operator, built-in, etc.):
    Extend eval_expr() or _eval_python_expr() in Interpreter.

Variable scoping:
    Global variables live in self.global_scope (a plain dict).
    Each FUNCTION call gets its own local_scope dict pre-filled with params.
    There is no closure support in the base implementation.
"""

import re
import os


class ReturnSignal(Exception):
    """
    Raised inside a FUNCTION body when a RETURN statement is executed.
    Carries the return value so the caller can retrieve it.
    """
    def __init__(self, value):
        self.value = value


class Interpreter:
    """
    Walks the AST(Abstract Syntax Tree) produced by Parser and executes each node.

    Usage:
        interp = Interpreter()
        interp.run(ast)
    """

    def __init__(self):
        self.global_scope = {}   # global variable namespace
        self.functions = {}      # name → FUNCTION node

    # ------------------------------------------------------------------ #
    # Public entry point                                                   #
    # ------------------------------------------------------------------ #

    def run(self, ast, scope=None):
        """Execute a list of AST nodes. Defaults to the global scope."""
        if scope is None:
            scope = self.global_scope
        for stmt in ast:
            self.execute(stmt, scope)

    # ------------------------------------------------------------------ #
    # Statement execution                                                  #
    # ------------------------------------------------------------------ #

    def execute(self, stmt, scope):
        """
        Dispatch on stmt["type"] and execute the corresponding action.

        To add a new statement type, add an elif branch here.
        """
        t = stmt["type"]

        # ---- SET x <- expr ---------------------------------------------
        if t == "SET":
            scope[stmt["var"]] = self.eval_expr(stmt["expr"], scope)

        # ---- INPUT varname ---------------------------------------------
        elif t == "INPUT":
            prompt = self.eval_expr(stmt["prompt"], scope) if stmt["prompt"] else ""
            try:
                raw = input(f"{prompt} " if prompt else "")
            except EOFError:
                raw = ""
            scope[stmt["var"]] = self._coerce(raw)

        # ---- DISPLAY expr ----------------------------------------------
        elif t == "DISPLAY":
            print(self.eval_expr(stmt["expr"], scope))

        # ---- IF condition THEN / ELSE ----------------------------------
        elif t == "IF":
            branch = stmt["true_body"] if self.eval_expr(stmt["condition"], scope) \
                     else stmt["false_body"]
            self.run(branch, scope)

        # ---- WHILE condition DO ----------------------------------------
        elif t == "WHILE":
            while self.eval_expr(stmt["condition"], scope):
                self.run(stmt["body"], scope)

        # ---- FOR var FROM start TO end ---------------------------------
        elif t == "FOR":
            start = int(self.eval_expr(stmt["start"], scope))
            end = int(self.eval_expr(stmt["end"], scope))
            for i in range(start, end + 1):
                scope[stmt["var"]] = i
                self.run(stmt["body"], scope)

        # ---- FUNCTION name(params) — store definition ------------------
        elif t == "FUNCTION":
            self.functions[stmt["name"]] = stmt

        # ---- RETURN expr -----------------------------------------------
        elif t == "RETURN":
            value = self.eval_expr(stmt["expr"], scope) if stmt["expr"] else None
            raise ReturnSignal(value)
        
        # --- CLEAR_CONSOLE -----------------------------------------------
        elif t == "CLEAR_CONSOLE":
           #use os.system('cls' if os.name == 'nt' else 'clear') for a more robust solution.
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear') 
        
<<<<<<< HEAD
        # ---- TRY ... CATCH [error_var] ... END TRY ---------------------
        elif t == "TRY":
            try:
                self.run(stmt["try_body"], scope)
            except (ReturnSignal, SystemExit):
                raise  # never swallow a RETURN or a sys.exit()
            except Exception as e:
                error_var = stmt.get("error_var")
                if error_var:
                    scope[error_var] = str(e)
                scope["$error"] = str(e)  # always available inside CATCH
                self.run(stmt.get("catch_body", []), scope)

        # ---- PASS — do nothing (placeholder for empty blocks) ----------
        elif t == "PASS":
            pass

=======
        elif t == "TRY":
            try:
                self.run(stmt["try_body"], scope)
            except Exception as e:
                # Store the error message in a special variable for the CATCH block
                scope["$error"] = str(e)
                catch_body = stmt.get("catch_body", stmt.get("false_body", []))
                self.run(catch_body, scope)
        
>>>>>>> 6b57c60b73b91e74482c9e44f1a09859fb26185e
        # ---- Unknown node type — ignore --------------------------------
        # Remove this branch to get strict runtime errors on unknown nodes.
        else:
            pass

    # ------------------------------------------------------------------ #
    # Expression evaluator                                                 #
    # ------------------------------------------------------------------ #

    def eval_expr(self, expr, scope):
        """
        Evaluate a sudo-code expression string and return a Python value.

        Supported expression forms:
          "hello"          — string literal  (quotes required for plain text)
          42 / 3.14        — numeric literal
          x                — variable lookup (raises NameError if not defined)
          name(a, b)       — function call
          x + y * 2        — arithmetic / comparison (via safe Python eval)
          x AND y          — logical operators (AND, OR, NOT, MOD)

        Rules enforced here:
          - Plain text must be quoted:  DISPLAY "hello"  not  DISPLAY hello
          - A bare name with no quotes is always a variable lookup.
            If the variable does not exist a RuntimeError is raised.

        To add new expression forms, extend this method or _eval_python_expr().
        """
        expr = expr.strip()
        if not expr:
            return None

        # ---- Quoted string literal  "hello"  or  'hello' ----------------
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # ---- Function call  name(arg1, arg2) ----------------------------
        func_match = re.match(r'^(\w+)\(([^)]*)\)$', expr)
        if func_match:
            fname = func_match.group(1)
            raw_args = func_match.group(2)
            args = [
                self.eval_expr(a.strip(), scope)
                for a in raw_args.split(",")
                if a.strip()
            ]
            return self._call_function(fname, args, scope)

        # ---- Numeric literal  42  or  3.14  --------------------------------
        try:
            return int(expr)
        except ValueError:
            pass
        try:
            return float(expr)
        except ValueError:
            pass

        # ---- Bare identifier  x  ----------------------------------------
        # A single plain word (no spaces, no operators) is a variable lookup.
        # Raises RuntimeError if the variable has not been defined.
        if re.match(r'^[A-Za-z_]\w*$', expr):
            # Allow Python built-in literals
            if expr == "True":
                return True
            if expr == "False":
                return False
            if expr == "None":
                return None
            if expr in scope:
                return scope[expr]
            raise RuntimeError(
                f"Variable '{expr}' is not defined. "
                f"Use quotes for text: \"{expr}\""
            )

        # ---- Arithmetic / comparison expression  x + 1,  x > 0, etc. ---
        return self._eval_python_expr(expr, scope)

    def _eval_python_expr(self, expr, scope):
        """
        Translate sudo-code operators into Python equivalents, then
        evaluate the expression safely using Python's eval().

        Safe context: only the current scope variables and a small set of
        safe built-ins are available — no __builtins__ access.

        To add a new operator or built-in, extend the replacements below
        or the safe_env dict.
        """
        # Translate sudo-code logical / arithmetic operators
        expr = re.sub(r'\bAND\b', 'and', expr)
        expr = re.sub(r'\bOR\b',  'or',  expr)
        expr = re.sub(r'\bNOT\b', 'not', expr)
        expr = re.sub(r'\bMOD\b', '%',   expr)

        # Build a safe evaluation namespace
        safe_env = dict(scope)
        safe_env.update({
            "True": True, "False": False, "None": None,
            # Add safe built-ins here:
            "abs":   abs,
            "len":   len,
            "str":   str,
            "int":   int,
            "float": float,
            "round": round,
        })

        try:
            return eval(expr, {"__builtins__": {}}, safe_env)
        except NameError as e:
            # A variable used in the expression was not defined
            raise RuntimeError(str(e).replace("name '", "Variable '").replace("' is not defined", "' is not defined"))
        except Exception:
            # Other eval errors (syntax, type, etc.) — return as plain string
            return expr

    # ------------------------------------------------------------------ #
    # Function calls                                                       #
    # ------------------------------------------------------------------ #

    def _call_function(self, name, args, caller_scope):
        """
        Look up a user-defined FUNCTION by name and call it with args.
        Creates a fresh local scope populated with parameter values.
        """
        # Handle built-in functions
        if name.upper() == "INPUT":
            prompt = args[0] if args else ""
            try:
                raw = input(f"{prompt} " if prompt else "")
            except EOFError:
                raw = ""
            return self._coerce(raw)

        if name not in self.functions:
            raise NameError(f"Undefined function: '{name}'")
        func = self.functions[name]
        local_scope = {
            param: (args[i] if i < len(args) else None)
            for i, param in enumerate(func["params"])
        }
        try:
            self.run(func["body"], local_scope)
        except ReturnSignal as ret:
            return ret.value
        return None

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _coerce(self, value):
        """
        Try to convert a string to int, then float, then keep as string.
        Used when reading INPUT values from the user.
        """
        for cast in (int, float):
            try:
                return cast(value)
            except ValueError:
                pass
        return value
