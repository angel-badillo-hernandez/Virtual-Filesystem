#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

cat_flags:set[str] = {
    "--help"
}

def cat(**kwargs):
    """   
    NAME
        cat 

    DESCRIPTION
        cat                 : concatenate FILE(s) to standard output
            --help          : displays how to use the cat command
            
    EXAMPLES
        `cat <file name>`   : copy file contents to standard output
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""
    
    # Check if invalid flags are present
    if not flags.issubset(cat_flags):
        result = invalidFlagsMsg(cat, cat_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = cat.__doc__
    # If other valid flags or none
    else:
        contents:list[str] = []

        for param in params:
            
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            if os.path.isfile(param):
                with open(param, mode="r") as file:
                    contents.append(file.read())
            elif os.path.isdir(param):
                contents.append(f"{cat.__name__}: '{param}': Is a directory")
            else:
                contents.append(f"{cat.__name__}: cannot access '{param}': No such file or directory")
        result = '\n'.join(contents)

    return result    

if __name__ == "__main__":
    s = cat(params=["hi", ".gitignore", "~/hi.txt"])
    print(s)