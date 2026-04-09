"""
sudo_interpreter.py — command-line entry point for the sudo code language.

Usage:
    python sudo_interpreter.py <file.sudo>

The actual language implementation lives in the sudo_lang/ package:
    sudo_lang/nodes.py       — KEYWORDS and AST node factory
    sudo_lang/lexer.py       — tokeniser
    sudo_lang/parser.py      — recursive-descent parser
    sudo_lang/interpreter.py — AST walker / runtime
"""

import sys
from sudo_lang import run_file
from sudo_lang.parser import ParseError


def main():
    if len(sys.argv) < 2:
        print("Usage: python sudo_interpreter.py <file.sudo>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not filepath.endswith(".sudo"):
        print(f"Warning: '{filepath}' does not have a .sudo extension.")

    try:
        run_file(filepath)
    except FileNotFoundError:
        print(f"Error: File not found: '{filepath}'")
        sys.exit(1)
    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
