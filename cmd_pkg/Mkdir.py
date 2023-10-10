from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

mkdir_flags:set[str] = {
    "--help"
}

def mkdir(**kwargs)-> str:
    """
    NAME
        mkdir
        
    DESCRIPTION
        mkdir       : makes a new directory in the current directory
            --help  : displays how to use the mkdir command
        
    EXAMPLE
        `mkdir <name of directory>` 
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(mkdir_flags):
        result = invalidFlagsMsg(mkdir, mkdir_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = mkdir.__doc__
    # If other valid flags or none
    else:
        for param in params:
            
            try:
                fileSystem.make_dir(param)
            except(FileExistsError):
                result = f"{mkdir.__name__}: cannot create directory '{param}': File exists"
            except(FileNotFoundError):
                result = f"{mkdir.__name__}: cannot create directory '{param}': No such file or directory"
            except(PermissionError):
                result = f"{mkdir.__name__}: cannot create directory '{param}': Permission denied"

    return result

if __name__ == "__main__":
    s= mkdir(params=["/oof/a"], flags=[])
    print(s)