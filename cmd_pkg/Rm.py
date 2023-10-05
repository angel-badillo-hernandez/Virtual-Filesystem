#!/usr/bin/env python3
import os
import shutil
from glob import glob
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

rm_flags:set[str] = {
    "--help",
    "-r"
}

def rm(**kwargs)-> str:
    """
    NAME
        rm 
        
    DESCRIPTION
        rm                          : removes a file or directory
            -r                      : recursively removes all contents of a file/directory
            
    EXAMPLE
        `rm <filename>'             : removes a file or directory
        `rm --help'                 : displays how to use the rm command
        `rm -r <directory name>'    : removes a directory and its contents
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(rm_flags):
        result = invalidFlagsMsg(rm, rm_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = rm.__doc__
    # If other valid flags or none
    else:
        recursive:bool = "-r" in flags

        contents:list[str] = []

        for param in params:
            line:str = ""
            
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            try:
                # If -r flag enabled, recursively remove directories and their contents
                for match in glob(param):
                    if recursive and os.path.isdir(match):
                        shutil.rmtree(match)
                    else:
                        os.remove(match)
            except(FileNotFoundError):
                line = f"{rm.__name__}: cannot remove '{param}': No such file or directory"
            except(IsADirectoryError):
                line = f"{rm.__name__}: cannot remove '{param}': Is a directory"
            except(OSError):
                line = f"{rm.__name__}: cannot remove '{param}': Permission denied"
            contents.append(line)
        result = "\n".join(contents)

    return result

if __name__ == "__main__":
    s= rm(params=["hi.txt", "woo"], flags=["-r"])
    print(s)
    print("Be careful when testing this. Is mostly safe though.")