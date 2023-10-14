from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

mv_flags: set[str] = {"--help"}


def mv(**kwargs) -> str:
    """
    NAME
        mv

    DESCRIPTION
        mv            : moves a file or directory
            --help    : displays how to use the mv command

    EXAMPLE
       `mv <path to file> <path to destination>'
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(mv_flags):
        result = invalidFlagsMsg(mv, mv_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = mv.__doc__
    # If other valid flags or none
    else:
        if len(params) == 2:
            try:
                fileSystem.move(params[0], params[1])
            # If file not found or already exist
            except (FileNotFoundError, FileExistsError) as error:
                result = (
                    f"{mv.__name__}: cannot move '{error.filename}': {error.strerror}"
                )
            # If src and dest are the same
            except OSError as error:
                result = f"{mv.__name__}: '{error.filename}' is '{error.filename2}'"
        else:
            result = f"{mv.__name__}: missing file operand(s)"

    return result


if __name__ == "__main__":
    s = mv(params=["/home", "/fortnite"], flags=[])
    print(s)
