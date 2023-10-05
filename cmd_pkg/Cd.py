#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

cd_flags:set[str] = {
    "--help"
}

def cd(**kwargs)-> str:
    """
    NAME
        cd 
        
    DESCRIPTION
        cd           : changes the current directory to the specified directory
            --help   : displays how to use the cd command
        
    EXAMPLE
        `cd <path>`  : moves into the specified directory path
        `cd ~`       : changes the current directory to the home directory
        `cd ..`      : moves the current directory back one directory
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # If no param, default to user directory
    if not params:
        params.append("~")

    # Check if invalid flags are present
    if not flags.issubset(cd_flags):
        result = invalidFlagsMsg(cd, cd_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = cd.__doc__
    # If other valid flags or none
    else:
        # Too many arguments
        if len(params) > 1:
            result = f"{cd.__name__}: too many arguments"
        # 1 argument
        else:
            param:str = params[0]

            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)
            
            # Check if valid directory
            if os.path.isdir(param):
                os.chdir(param)
            else:
                result = f"{cd.__name__}: '{param}': No such directory"

    return result

if __name__ == "__main__":
    print(os.getcwd())

    s:str = cd(params=["~/projects"])

    print(s)

    print(os.getcwd())