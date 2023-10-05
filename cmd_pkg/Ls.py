#!/usr/bin/env python3
import os, stat, datetime, pwd, grp
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

RESET = "\033[0m"      # Reset text formatting and color
BOLD = "\033[1m"       # Bold text
DARK_GREEN = "\033[32m"     # Green text
BLUE = "\033[94m"      # Blue text
RED = "\033[91m"       # Red text

ls_flags:set[str] = {
    "-l",    
    "-a",
    "-h",
    "--help",
}

# Converts bytes to "human-readable" format
# Credits to:
# https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
def format_bytes(num_bytes:float)-> str:
    power:int = 2**10
    n:int = 0

    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while num_bytes > power:
        num_bytes /= power
        n += 1

    return f"{num_bytes:.1f}{power_labels[n]}" if n > 0 else f"{num_bytes:.0f}"

def calculate_total(directory_path):
    total_blocks = 0
    
    for path in os.scandir(directory_path):
        total_blocks += os.stat(path).st_blocks

    return total_blocks

def ls(**kwargs)-> str:
    """
    NAME
        ls 
        
    DESCRIPTION
        ls          : lists the contents of a directory
            --help  : displays how to use the ls command
            -l      : lists the contents of a directory in long format
            -a      : lists the contents of a directory including hidden files
            -h      : lists the contents of a directory in human readable format
    
    EXAMPLE
        `ls'        : lists the contents of a directory in shor format
        `ls -l'     : lists the contents of a directory in long format
        `ls -lah`   : lists the contents of a directory in long format including hidden files in human readable format
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    stdout:bool = kwargs.get("stdout", True)
    result:str = ""

    # If no params, default to cwd
    if not params:
        params.append(os.getcwd())


    # Check if invalid flags are present
    if not flags.issubset(ls_flags):
        result = invalidFlagsMsg(ls, ls_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = ls.__doc__
    # If other valid flags or none
    elif stdout:
        showHidden:bool = "-a" in flags
        longListing:bool = "-l" in flags
        humanReadable:bool = "-h" in flags

        contents:list[list[str]] = []

        # Perform ls command for all params (directories)
        for param in params:
            
            line:list[str] = []

            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            # Provide error message if invalid directory
            if not os.path.exists(param):
                contents.append(f"{ls.__name__}: cannot access '{param}': No such file or directory")
            else:
                # Show directory name if multiple parameters
                if not len(params) == 1:
                    contents.append(f"{param}:")

                if longListing:
                    contents.append(f"total {calculate_total(param)}")

                for entry in os.scandir(param):
                    RED_MODE = False
                    # If '-a' flag enabled, show hidden files
                    if not entry.name.startswith(".") or showHidden:

                        # if '-l' flag enabled, show long listing
                        if longListing:
                            entryStats = os.stat(f"{param}/{entry.name}")
                            mode:str = stat.filemode(entryStats.st_mode)
                            
                            
                            if entryStats.st_mode & stat.S_IXUSR:
                                line.append(RED + mode + RESET)
                                RED_MODE = True
                            else:
                                line.append(DARK_GREEN + mode + RESET)

                            # permissions
                            # line.append(mode)
                            line.append("\t")
                            
                            # hard links
                            line.append(str(entryStats.st_nlink))
                            line.append('\t')

                            # owner and group id
                            uid:int = entryStats.st_uid
                            gid:int = entryStats.st_gid
                            u_name:str = pwd.getpwuid(uid).pw_name
                            g_name:str = grp.getgrgid(gid).gr_name

                            line.append(u_name)
                            line.append('\t')
                            line.append(g_name)
                            line.append('\t')

                            # if '-h' flag enabled, show human readable sizes
                            if humanReadable:
                                line.append(str(format_bytes(entryStats.st_size)))
                                line.append('\t')
                            else:
                                line.append(str(entryStats.st_size))
                                line.append('\t')

                            # time of last modification
                            mtime:str = datetime.datetime.fromtimestamp(entryStats.st_mtime).isoformat(sep='\t', timespec="minutes")
                            line.append(mtime)
                            line.append('\t')
                            # if ls flags are subset of flags print in contents in colors
                            if RED_MODE and not os.path.isdir(f"{param}/{entry.name}"):
                                entryStats = os.stat(f"{param}/{entry.name}")
                                entryStats.st_mode & stat.S_IXUSR
                                line.append(RED +  entry.name + RESET)
                            elif os.path.isdir(f"{param}/{entry.name}"):
                                line.append(BLUE + BOLD + entry.name + RESET)
                            else:
                                line.append(DARK_GREEN +  entry.name + RESET)

                            line.append('\n')
                        # else show short listing
                        else:
                            # Name
                            entryStats = os.stat(f"{param}/{entry.name}")
                            if os.path.isdir(f"{param}/{entry.name}"):
                                line.append(BLUE + BOLD + entry.name + RESET)
                            else:
                                line.append(DARK_GREEN +  entry.name + RESET)

                            line.append('\t')
                        
                      
                            
                contents.append(''.join(line))
            
            result = "\n".join(contents)
    else:
        showHidden:bool = "-a" in flags
        longListing:bool = "-l" in flags
        humanReadable:bool = "-h" in flags

        contents:list[list[str]] = []

        # Perform ls command for all params (directories)
        for param in params:
            
            line:list[str] = []

            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            # Provide error message if invalid directory
            if not os.path.exists(param):
                contents.append(f"{ls.__name__}: cannot access '{param}': No such file or directory")
            else:
                # Show directory name if multiple parameters
                if not len(params) == 1:
                    contents.append(f"{param}:")

                if longListing:
                    contents.append(f"total {calculate_total(param)}")

                for entry in os.scandir(param):
                    # If '-a' flag enabled, show hidden files
                    if not entry.name.startswith(".") or showHidden:

                        # if '-l' flag enabled, show long listing
                        if longListing:
                            entryStats = os.stat(f"{param}/{entry.name}")
                            mode:str = stat.filemode(entryStats.st_mode)

                            # permissions
                            line.append(mode)
                            line.append("\t")
                            
                            # hard links
                            line.append(str(entryStats.st_nlink))
                            line.append('\t')

                            # owner and group id
                            uid:int = entryStats.st_uid
                            gid:int = entryStats.st_gid
                            u_name:str = pwd.getpwuid(uid).pw_name
                            g_name:str = grp.getgrgid(gid).gr_name

                            line.append(u_name)
                            line.append('\t')
                            line.append(g_name)
                            line.append('\t')

                            # if '-h' flag enabled, show human readable sizes
                            if humanReadable:
                                line.append(str(format_bytes(entryStats.st_size)))
                                line.append('\t')
                            else:
                                line.append(str(entryStats.st_size))
                                line.append('\t')

                            # time of last modification
                            mtime:str = datetime.datetime.fromtimestamp(entryStats.st_mtime).isoformat(sep='\t', timespec="minutes")
                            line.append(mtime)
                            line.append('\t')
                            
                            line.append(entry.name)
                            line.append('\n')
                        # else show short listing
                        else:
                            line.append(entry.name)
                            line.append('\n')
                        
                      
                            
                contents.append(''.join(line))
            
            result = "\n".join(contents)
    return result

if __name__ == "__main__":
    print(ls(flags=["-lah"], params=["~/"]))