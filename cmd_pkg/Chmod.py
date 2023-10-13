import os, sys, stat
from . import fileSystem
from stat import *
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

chmod_flags: set[str] = {
    "--help,",
}

permissions: set[str] = {
    "r": stat.S_IRUSR,  # Read permission (user)
    "w": stat.S_IWUSR,  # Write permission (user)
    "x": stat.S_IXUSR,  # Execute permission (user)
}


def chmod(**kwargs) -> str:
    """
    NAME
        chmod

    DESCRIPTION
        all files/directories have specific permissions that determine who can read, write, and execute

            owner | group | others
            ----------------------
            drwx  | rwx   | rwx
            ----------------------

            d = directory
            r = read
            w = write
            x = execute


        chmod              : changes permissions for a file/directory
             --help        : Displays the help page for chmod
             7             : rwx | 111 |
             6             : rw- | 110 |
             5             : r-x | 101 |
             4             : r-- | 100 |
             3             : -wx | 011 |
             2             : -w- | 010 |
             1             : --x | 001 |
             0             : --- | 000 |

    EXAMPLE
        `chmod 777 <file>` : file is now readable, writeable, andexecutable for everyone
        `chmod 644 <file>` : file is now readable and writable for the owner, and readable for everyone else
        `chmod 755 <file>` : file is now readable, writeable, and executable for the owner, and readable and executable for everyone else
    """
    # path
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""
    message: str = ""
    # \ how to change permissions
    # permissions:list[str] = kwargs.get("permissions", [])
    if not params:
        params.append(os.getcwd())
    # Check if invalid flags are present
    if not flags.issubset(chmod_flags):
        result = invalidFlagsMsg(chmod, chmod_flags, flags)
    # Provide help info if --help flag present
    if "--help" in flags:
        result = "".join(chmod.__doc__)

    else:
        try:
            if len(params) > 1:
                permissions = params[0]
                path = params[1]
                # Convert the permissions string to an integer (e.g., "755" -> 0o755)
                # for path in params:
                mode = int(permissions, 8)
                # Apply the new permisssions to the file
                result = fileSystem.chmod(path, mode)
                message = "".join(
                    f"Changed permissions of {params[1]} to {permissions}."
                )
                return message
        except ValueError:
            message = "".join(
                "Invalid permissions format. Please provide octal permissions like '777' or '644'"
            )
        except PermissionError:
            message = "".join(
                "Permission denied. You do not have permission to change the permissions of '{params}'."
            )
        return message
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(chmod.__doc__)
        sys.exit(1)
    chmod(params=sys.argv[2], permissions=sys.argv[1])
