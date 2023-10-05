#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

sort_flags:set[str] = {
    "--help"
}

def sort(**kwargs)-> str:
    """
    NAME
        sort
        
    DESCRIPTION
        sort             : used to sort a file, arranging the records in a particular order
            --help       : displays how to use the sort command
        
    EXAMPLE 
        `sort <file>'   : sorts the specified file
        `sort  --help`  : displays how to use the sort command
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    stdin:bool = kwargs.get("stdin", True)
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(sort_flags):
        result = invalidFlagsMsg(sort, sort_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = sort.__doc__
    # If valid flags, and expect data from stdin
    elif stdin:
        contents:list[str] = []

        for param in params:
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)
            
            text:list[str] = []
            data:str = ""
            
            try:
                with open(param, "r") as infile:
                    data = infile.read()
            except(FileNotFoundError) as e:
                return f"{sort.__name__}: cannot access '{param}': No such file or directory"

            text = data.splitlines()
            text.sort()

            contents.append('\n'.join(text))

        result = '\n'.join(contents)
    # If expect data from file or pipe
    else:
        contents:list[str] = []

        for param in params:
            text:list[str] = param.splitlines()
            text.sort()

            contents.append('\n'.join(text))

        result = '\n'.join(contents)
        
    return result

if __name__ == "__main__":
    print(sort(params=["README.md"], flags=[], stdin=True))