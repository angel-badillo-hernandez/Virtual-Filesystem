#!/usr/bin/env python3
import os, shutil
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

cp_flags:set[str] = {
    "--help"
}

def cp(**kwargs)-> str:
    """
    NAME
        cp
        
    DESCRIPTION
        cp          : copies a file or directory do a new location
            --help  : displays how to use the cp command
        
    EXAMPLE
        `cp <file/directory to copy> <path to destination>'
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(cp_flags):
        result = invalidFlagsMsg(cp, cp_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = cp.__doc__
    # If other valid flags or none
    else:
        if len(params) == 2:
            for i in range(0, len(params)):
                # Replace tilde with user directory
                if params[i].startswith("~"):
                    params[i] = params[i].replace("~", os.path.expanduser("~"), 1)
            try:
                shutil.copyfile(params[0], params[1])
            except(FileNotFoundError, IsADirectoryError) as error:
                result = f"{cp.__name__}: cannot copy '{error.filename}': {error.strerror}"
        else:
            result = f"{cp.__name__}: missing file operand(s)"
            
    return result

if __name__ == "__main__":
    s= cp(params=["~", "~/Fort/w2.txt"], flags=[])
    print(s)