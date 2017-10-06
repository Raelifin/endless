from typing import Callable

# TYPES

Input = Callable[[], str]
Output = Callable[[str], None]
MainFunction = Callable[[Input, Output], None]

# FUNCTIONS

def get_input_from_stdin() -> str:
    result = ""
    while result == "":
        result = input("> ")
    return result

def print_to_stdout(text: str) -> None:
    print(text)

def get_int_input(range_: range, get_input: Input, output: Output) -> int:
    result = None
    while result is None:
        try:
            result = int(get_input())
        except ValueError:  # type: ignore
            output("That is not a valid integer.")
            continue
        if result not in range_:
            output("That choice is not valid. (Valid choices are {})".format(','.join([str(x) for x in range_])))
            result = None
    return result
