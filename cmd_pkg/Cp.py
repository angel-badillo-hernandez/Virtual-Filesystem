#!/usr/bin/env python3
from . import fileSystem
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
            try:
                fileSystem.copy_file(params[0], params[1])
            except(FileNotFoundError, IsADirectoryError) as error:
                result = f"{cp.__name__}: cannot copy '{error.filename}': {error.strerror}"
        else:
            result = f"{cp.__name__}: missing file operand(s)"
            
    return result

if __name__ == "__main__":
    s= cp(params=["/home/angel/Fortnite.exe", "/fort.exe"], flags=[])
    print(s)