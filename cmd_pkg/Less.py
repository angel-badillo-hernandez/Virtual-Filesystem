#!/usr/bin/env python3
import os
import sys
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

CLEAR = "\033c"

less_flags:set[str] = {"--help"}

def less(**kwargs):
    """
    NAME
        less
    
    DESCRIPTION
        less               : display the contents of a file one page at a time
            --help         : displays how to use the less command
            
    EXAMPLES
        `less <file name>` : copy the contents of the file to standard output
        """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = CLEAR
    message:str = ""
    contents:list[str] = []
    # Check if invalid flags are present
    if not flags.issubset(less_flags):
        result = invalidFlagsMsg(less, less_flags, flags)
    # Provide help info if --help flag present
    if "--help" in flags:
        result = less. __doc__
        
     
    # If other valid flags or none


    try:
        # if len(params) > 0:
        for param in params:
            #print(CLEAR)
            os.system('clear' if os.name == 'posix' else 'cls')
            # filename = params[0]
            if os.path.isfile(param):
                with open(param, 'r') as file:
                    lines = file.readlines()
                    num_lines = len(lines)
                    current_line = 0
                    lines_per_page = 10  # Number of lines to display per page

                    while True:
                        print(CLEAR)
                        #os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal screen

                        for i in range(current_line, current_line + lines_per_page):
                            if i < num_lines:
                                print(lines[i].rstrip())

                        print("\n-- Press 'q' to quit, 'f' for next page, 'b' for previous page --")

                        user_input = input()
                        #  return to terminal screen
                        if user_input == 'q':
                            break
                        # move forward a page
                        elif user_input == 'f':
                            current_line += lines_per_page 
                            if current_line >= num_lines:
                                current_line = num_lines - 1
                        # move backward a page
                        elif user_input == 'b':
                            current_line -= lines_per_page
                            if current_line < 0:
                                current_line = 0
                        print(CLEAR)
                        #os.system('clear' if os.name == 'posix' else 'cls')
    except(FileNotFoundError) as error:
        result = f"{less.__name__}: cannot access '{error.filename}': {error.strerror}"
           
    return result
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python less.py <filename>")
        sys.exit(1)

    less_output = less(params=["facts.txt"])
    print(less_output)  # Print the captured output