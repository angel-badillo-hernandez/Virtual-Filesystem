from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

pwd_flags:set[str] = {
    "--help"
}

def pwd(**kwargs)-> str:
    """
    NAME
        pwd
    
    DESCRIPTION
        pwd             : prints the current working directory
            --help      : displays how to use the pwd command
   
    EXAMPLE
        `pwd'           : prints the current working directory
        `pwd --help'    : displays how to use the pwd command
    """
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(pwd_flags):
        result = invalidFlagsMsg(pwd, pwd_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = pwd.__doc__
    # If other valid flags or none
    else:
        result = fileSystem.get_cwd()
    
    return result

if __name__ == "__main__":
    fileSystem.set_cwd("/home/angel/")
    print(pwd())