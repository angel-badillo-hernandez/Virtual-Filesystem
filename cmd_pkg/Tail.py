#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

tail_flags:set[str] = {
    "--help"
}

def tail(**kwargs):
    """   
    NAME
        tail 

    DESCRIPTION
        tail                : display the last 10 lines of a file
            --help          : displays how to use the tail command
            -<n>            : displays the last n lines of a file
            
    EXAMPLES
        `tail <file name>`   : copy the last 10 lines of the file contents to standard output
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = set(kwargs.get("flags", []))
    stdin:bool = kwargs.get("stdin", True)
    result:str = ""
    numDisplayLines:int = 10
    
    # Check for -n flag
    if len(flags) == 1 and not "--help" in flags:
        numFlag = flags.pop()
        try:
            numDisplayLines = int(numFlag.removeprefix("-"))
        except(ValueError) as e:
            return f"{tail.__name__}: invalid option -- {numFlag}\nTry '{tail.__name__} --help for more information."
    # When n flag not present
    else:
        flags = tockenizeFlags(flags)
    
    # Check if invalid flags are present
    if not flags.issubset(tail_flags):
        result = invalidFlagsMsg(tail, tail_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = tail.__doc__
    # If other valid flags and expect data from stdin
    elif stdin:
        contents:list[str] = []
        for param in params:
            
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            if os.path.isfile(param):
                with open(param, mode="r") as file:
                    lines = file.readlines()  # Read all lines into a list
                    last_n_lines = lines[-numDisplayLines:]  # Get the last n lines or fewer

                    for line in last_n_lines:
                        line = line.strip()
                        contents.append(line)
                    else:
                        break  
                           
            elif os.path.isdir(param):
                contents.append(f"{tail.__name__}: '{param}': Is a directory")
            else:
                contents.append(f"{tail.__name__}: cannot access '{param}': No such file or directory")
                
        result = '\n'.join(contents)
    # If other valid flags and expect data from pipe or file redirect
    else:
        contents:list[str] = []

        for param in params:
            text:list[str] = param.splitlines()
            last_n_lines = text[-numDisplayLines:] # Get the last n lines or fewer

            for line in last_n_lines:
                line = line.strip()
                contents.append(line)
        result = '\n'.join(contents)

    return result    

if __name__ == "__main__":
    s = tail(params=["facts.txt"])
    print(s)