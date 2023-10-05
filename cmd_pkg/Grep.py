#!/usr/bin/env python3
import sys
import os
import re 
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg
from rich import print

grep_flags:set[str] = {
    "--help", "-c", "-i", "-v", "-l",
}
def grep(**kwargs)-> str:
    # print(kwargs)
    """
    NAME
        grep
        
    DESCRIPTION
        grep                    : prints out the lines in a file that match a given pattern
            --help              : displays how to use the grep command
            -c                  : prints the number of lines in a file that match a given pattern
            -i                  : ignores upper and lower case when searching for a pattern
            -v                  : prints lines that do not match the pattern
            -l                  : prints only the names of files that contain at least one matching line
    
    EXAMPLE
        `grep python README.md' : prints out the lines in README.md that contain the word "python"
            
    """
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    params:list[str] = kwargs.get("params", [])
    stdin:bool = kwargs.get("stdin", True)
    result:str = ""
    
    # Check if invalid flags are present
    if not flags.issubset(grep_flags):
        result = invalidFlagsMsg(grep, grep_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = "".join(grep.__doc__)
       
    
    elif stdin:
        ignore_case:bool = "-i" in flags
        count_only:bool = "-c" in flags
        invert_match:bool = "-v" in flags
        list_file:bool = "-l" in flags
        
        contents:list[list[str]] = []
        count:int = 0
        # print(kwargs)
        try:
            if len(params) >= 2:
                pattern = params[0]
                paths = params[1:]

                for path in paths:
                    if os.path.isfile(path):
                        with open(path, 'r') as file:
                            line_number = 1
                            for line in file:
                                line = line.strip()
                                match = False

                                if ignore_case:
                                    pattern = re.escape(pattern)
                                    if re.search(pattern, line, re.IGNORECASE):
                                        match = True
                                         
                                elif pattern in line:
                                    match = True
                                   

                                if match and not invert_match:
                                    if not list_file:
                                        contents.append(f'{os.path.abspath(path)}: {line_number}: {line}')
                                    elif list_file:
                                        contents.append(f'{os.path.abspath(path)}')
                                        
                                    count += 1
                                elif not match and invert_match:
                                    if not count_only:
                                        contents.append(f'{os.path.abspath(path)}: {line_number}: {line}')

                                line_number += 1

                if count_only:
                    return str(count)

                if list_file:
                    # contents = [os.path.abspath(path) for path in paths]
                    result = "\n".join(set(contents)) 
                    
                else:
                    result = "\n".join(contents)
                    
        except FileNotFoundError as e:
            result = f"Error: '{e.filename}' not found."

    return result

if __name__ == "__main__":


    # if len(sys.argv) != 3:
    #     print(grep.__doc__)
    #     sys.exit(1)
    # grep(pattern=sys.argv[1], path=sys.argv[2])
    print(grep(params=["Angel","README.md", ]))