#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

head_flags:set[str] = {
    "--help"
}

def head(**kwargs):
    """   
    NAME
        head 

    DESCRIPTION
        head               : display the first 10 lines of a file         
            --help         : displays how to use the head command
            -<n>           : displays the first n lines of a file
            
    EXAMPLES
        `head <file name>` : copy the first 10 lines of the file contents to standard output
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
            return f"{head.__name__}: invalid option -- {numFlag}\nTry '{head.__name__} --help for more information."
    # When n flag not present
    else:
        flags = tockenizeFlags(flags)

    # Check if invalid flags are present
    if not flags.issubset(head_flags):
        result = invalidFlagsMsg(head, head_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = head.__doc__
    # If other valid flags and expect data from stdin
    elif stdin:
        contents:list[str] = []
        for param in params:
            
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            if os.path.isfile(param):
                with open(param, mode="r") as file:
                    for line_number, line in enumerate(file, start=1):
                        if line_number <= numDisplayLines:  # Only read the first n lines
                            line = line.strip()
                            contents.append(line)
                        else:
                            break  # Stop reading after the first n lines
                            
            elif os.path.isdir(param):
                contents.append(f"{head.__name__}: '{param}': Is a directory")
            else:
                contents.append(f"{head.__name__}: cannot access '{param}': No such file or directory")
                
        result = '\n'.join(contents)
    # if other valid flags and expect data from pipe or file redirect
    else:
        contents:list[str] = []
        for param in params:
            
            text:list[str] = param.splitlines()

            for line_number, line in enumerate(text, start=1):
                if line_number <= numDisplayLines: # Only get the first n lines
                    line = line.strip()
                    contents.append(line)
                else:
                    break # Stop reading after the first n lines

        result = '\n'.join(contents)
    return result    

if __name__ == "__main__":
    s = head(params=["facts.txt"])
    print(s)