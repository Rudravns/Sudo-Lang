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
from sudo_lang.lexer import tokenise
from sudo_lang.parser import ParseError, Parser
from sudo_lang.util import ParseError, RuntimeError

def main():
    if len(sys.argv) < 2:
        print("Usage: python sudo_interpreter.py <file.sudo>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not filepath.endswith(".sudo"):
        print(f"Warning: '{filepath}' does not have a .sudo extension.")

    try:
        run_file(filepath)
        #print the tokenised and parsed AST for debugging
        if True:  # Set to True to enable token/AST debug output
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.readlines()
                print("Tokenised lines:")
                for line in source:
                    print(f"{line!r:40s} -> {tokenise(line)}")
                parser = Parser(source)
                
    except FileNotFoundError:
        print(f"Error: File not found: '{filepath}'")
        sys.exit(1)
    except ParseError as e:
        pass
        raise ParseError(e.args[0], e.line_num, exit_after=True)
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}", exit_after=True)
        


if __name__ == "__main__":
    main()
