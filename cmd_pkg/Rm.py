from . import fileSystem
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

rm_flags:set[str] = {
    "--help",
    "-r",
    "-f"
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
        force:bool = "-f" in flags

        contents:list[str] = []

        for param in params:
            line:str = ""

            try:
                # If -r flag enabled, recursively remove directories and their contents
                if recursive and fileSystem.is_dir(param):
                    if not force:
                        response:str = input(f"rm: remove '{param}'? [y/n] ")
                        if response == "y":
                            fileSystem.remove_tree(param)
                    else:
                        fileSystem.remove_tree(param)
                else:
                    if not force:
                        response:str = input(f"rm: remove '{param}'? [y/n] ")
                        if response == "y":
                            fileSystem.remove(param)
                    else:
                        fileSystem.remove(param)
            except(FileNotFoundError):
                line = f"{rm.__name__}: cannot remove '{param}': No such file or directory"
            except(IsADirectoryError):
                line = f"{rm.__name__}: cannot remove '{param}': Is a directory"
            contents.append(line)
        result = "\n".join(contents)

    return result

if __name__ == "__main__":
    s= rm(params=["home/leslie", "home/angel/f"], flags=["-f"])
    print(s)