#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

wc_flags:set[str] = {
    "--help",
    "-l",
    "-m",
    "-w"
}

def wc(**kwargs)-> str:
    """
    NAME
        wc 
        
    DESCRIPTION
        wc                  : prints out the number of lines, words, and bytes in a file
            -l              : prints the number of lines in a file
            -m              : prints the number of bytes in a file
            -w              : prints the number of words in a file
            --help          : displays how to use the wc command
        
    EXAMPLE
        `wc README.md'      : prints out the number of lines, words, and bytes in README.md
        `wc -l README.md'   : prints out the number of lines in README.md
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    stdin:bool = kwargs.get("stdin", True)
    result:str = ""
    
    # Set all flags to true
    if not flags:
        flags = wc_flags.difference({"--help"})

    # Check if invalid flags are present
    if not flags.issubset(wc_flags):
        result = invalidFlagsMsg(wc, wc_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = wc.__doc__
    # If valid flags and expect data from stdin
    elif stdin:
        showLines:bool = "-l" in flags
        showChars:bool = "-m" in flags
        showWords:bool = "-w" in flags

        contents:list[str] = []

        for param in params:
            
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            if os.path.isfile(param):
                with open(param, mode="r") as file:
                    wcCounts:list[str] = []

                    fileData:str = file.read()
                    byteCount:int = len(fileData.encode('utf-8'))
                    lines:list[str] = fileData.splitlines(True)
                    lineCount:int = len(lines)
                    wordCount:int = 0
                    for line in lines:
                        wordCount += len(line.split())

                    if showLines:
                        wcCounts.append(str(lineCount))
                    if showWords:
                        wcCounts.append(str(wordCount))
                    if showChars:
                        wcCounts.append(str(byteCount))
                    wcCounts.append(param)
                    contents.append('\t'.join(wcCounts))
                    
            elif os.path.isdir(param):
                contents.append(f"{wc.__name__}: '{param}': Is a directory")
            else:
                contents.append(f"{wc.__name__}: cannot access '{param}': No such file or directory")
        result = '\n'.join(contents)
    # If expect data from input file redirect or pipe
    else:
        showLines:bool = "-l" in flags
        showChars:bool = "-m" in flags
        showWords:bool = "-w" in flags

        contents:list[str] = []

        for param in params:
            wcCounts:list[str] = []

            byteCount:int = len(param.encode('utf-8'))
            lines:list[str] = param.splitlines(True)
            lineCount:int = len(lines)
            wordCount:int = 0
            for line in lines:
                wordCount += len(line.split())

            if showLines:
                wcCounts.append(str(lineCount))
            if showWords:
                wcCounts.append(str(wordCount))
            if showChars:
                wcCounts.append(str(byteCount))
        contents.append('\t'.join(wcCounts))
        result = '\n'.join(contents)
    return result

if __name__ == "__main__":
    print(wc(params=["README.md"], flags=["-m"]))