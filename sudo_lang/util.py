<<<<<<< HEAD
from colorama import Fore, Style, init


class SudoLangError(Exception):
    """
    Base class for all SudoLang errors.
    Prints a coloured error message to the console, then exits with code 1.
    Inherits from Exception so it can also be used with raise if needed.
    """
    def __init__(self, message, line_num=None):
        super().__init__(message)
        init(autoreset=True)
        if line_num is not None:
            print(f"{Fore.RED}Error at line {line_num}: {message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}")
        exit(1)


class KEYWORD_NOT_FOUND(SudoLangError):
    """Called when the parser sees a word it does not recognise as a keyword."""
    def __init__(self, keyword, line_num):
        super().__init__(f"Unknown keyword '{keyword}'", line_num)
=======
from colorama import Fore, Back, Style, init


class SudoLangError():
    """Base class for all SudoLang errors.\n   All errors inherit from this, so you can catch it to handle any error.
    \n prints and then exits the program with a non-zero status code, indicating an error occurred. with the line number and error message in red text for visibility.
    """
    def __init__(self, message, line_num=None):
        init(autoreset=True)  # Initialize colorama
        if line_num is not None:
            print(f"{Fore.RED}Error at line {line_num}: {message}")
        else:
            print(f"{Fore.RED}Error: {message}")
        exit(1)



class KEYWORD_NOT_FOUND(SudoLangError):
    """Raised when a keyword is not found in the source code."""
    def __init__(self, keyword, line_num):
        message = f"Keyword '{keyword}' not found at line {line_num}."
        super().__init__(message)
        


       
>>>>>>> 6b57c60b73b91e74482c9e44f1a09859fb26185e
