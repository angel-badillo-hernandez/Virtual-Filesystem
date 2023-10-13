from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

rmdir_flags: set[str] = {"--help"}


def rmdir(**kwargs) -> str:
    """
    NAME
        rm

    DESCRIPTION
        rmdir                     : deletes a directory
             --help               : Displays the help page for rmdir
    EXAMPLE
        `rmdir <directory name>'  : removes the directory from the current working directory


    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(rmdir_flags):
        result = invalidFlagsMsg(rmdir, rmdir_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = rmdir.__doc__
    # If other valid flags or none
    else:
        contents: list[str] = []

        for param in params:
            line: str = ""

            try:
                fileSystem.remove_dir(param)
            except FileNotFoundError:
                line: str = f"{rmdir.__name__}: failed to remove '{param}': No such file or directory"
            except NotADirectoryError:
                line: str = (
                    f"{rmdir.__name__}: failed to remove '{param}': Not a directory"
                )
            except OSError as e:
                line = (
                    f"{rmdir.__name__}: failed to remove '{param}': Directory not empty"
                )
            if line:
                contents.append(line)
        result = "\n".join(contents)

    return result


if __name__ == "__main__":
    fileSystem.csv_to_table("fakeFileData.csv")
    s = rmdir(params=["/", "w", "/sys", "fofofofo"])
    print(s)
