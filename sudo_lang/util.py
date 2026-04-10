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
        


       
