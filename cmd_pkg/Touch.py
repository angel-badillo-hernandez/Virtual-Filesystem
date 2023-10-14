import sys
from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

touch_flags: set[str] = {"--help"}


def touch(**kwargs) -> str:
    """
    NAME
        touch

    DESCRIPTION
        touch               : create a new empty file in the current directory with any specifited extension or none
            --help          : displays how to use the touch command

    EXAMPLE
        `touch <file.txt>`  : creates a new empty text file
        `touch <file.py>`   : creates a new empty python file
        `touch ~/<file.txt>`: creates a new empty text file in the home directory
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(touch_flags):
        result = invalidFlagsMsg(touch, touch_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = touch.__doc__

        # If other valid flags or none
    else:
        for param in params:
            try:
                fileSystem.touch(param)
            except (FileNotFoundError, NotADirectoryError):
                result = f"{touch.__name__}: cannot touch '{param}': No such file or directory"

    return result


if __name__ == "__main__":
    s = touch(params=sys.argv[1:], flags=[])
    print(s)
