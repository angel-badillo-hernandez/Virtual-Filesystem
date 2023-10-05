#!/usr/bin/env python3
import os,sys, socket, getpass, shutil
from time import sleep
import cmd_pkg
from getch import Getch
from ParseCommand import parseCommand
from ParseCommand import ShellCommand
from cmd_pkg.TockenizeFlags import tockenizeFlags
from cmd_pkg.InvalidFlagsMsg import invalidFlagsMsg

RESET = "\033[0m"      # Reset text formatting and color
BOLD = "\033[1m"       # Bold text
GREEN = "\033[92m"     # Green text
YELLOW = "\033[93m"    # Yellow text
CYAN = "\033[36m"      # Blue text
PURPLE = "\033[35m"    # Purple text


history_flags:set[str] = {
    "--help",
    "-c"
}

def history(historyList:list[str], **kwargs)->str:
    """
    NAME
        history
        
    DESCRIPTION
        history             : prints out the history of commands that have been entered by the user
            --help          : displays how to use the history command
            -c              : clears the history of commands entered by the user
            
    EXAMPLE
        `history`           : prints the all commands entered by the user
        `history   10`      : prints the first 10 commands entered by the user
        `history   --help`  : displays how to use the history command
        `history   -c`      : clears the history of commands entered by the user
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # If no params, default to display full history
    if not params:
        params.append(len(historyList))

    # Check if invalid flags are present
    if not flags.issubset(history_flags):
        result = invalidFlagsMsg(history, history_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = history.__doc__
    elif "-c" in flags:
        historyList.clear()
    else:
         # If more than 1 argument
        if len(params) > 1:
            result = f"{history.__name__}: too many arguments"
        # 
        else:
            contents:list[str] = []
            
            try:
                numLines:int = int(params[0])
                for index in range(0, numLines):
                    contents.append(f"\t{index+1} {historyList[index]}")
                result = "\n".join(contents)
            # If param is not positive integer, result is error message
            except(ValueError):
                result = f"{history.__name__}: {params[0]}: invalid option"
                
    return result

def prompt()->str:
    """
    Returns a linux-like prompt.
    """
    username = PURPLE + BOLD + getpass.getuser() + RESET
    hostname = YELLOW + socket.gethostname() + RESET
    directory = CYAN + os.getcwd() + RESET

    return f"{username}@{hostname}:{directory}{GREEN+BOLD}$: {RESET}"

def print_cmd(commandStr:str)->str:
    """ This function "cleans" off the command line, then prints
        whatever cmd that is passed to it to the bottom of the terminal.
    """
    terminal_width = shutil.get_terminal_size().columns
    padding = " " * terminal_width
    sys.stdout.write("\r"+padding)
    sys.stdout.write("\r"+prompt()+commandStr)
    sys.stdout.flush()
 

historyFileName:str = ".myHistory"

# Store history here
historyList:list[str] = []
# Current index of history
movingIndex:int = 0

# Open and read history file, if it exists
if os.path.isfile(historyFileName):
    with open(historyFileName, "r") as historyFile:
        historyList = historyFile.read().splitlines()
    if historyList:
        movingIndex = len(historyList)

getch:Getch = Getch()                             # create instance of our getch class

if __name__ == '__main__':
    commandStr = ""                                # empty commandStr variable

                              # print to terminal
    
    while True:                             # loop forever
        print_cmd(commandStr)               # print the commandStr (with our prompt
        char = getch()                      # read a character (but don't print)

        if char == '\x03': # ctrl-c
            with open(historyFileName, "w") as historyFile:
                historyFile.write('\n'.join(historyList))
            print_cmd(f"{commandStr}\n")
            cmd_pkg.exit()
        
        elif char == '\x7f':                # back space pressed
            commandStr = commandStr[:-1]
            print_cmd(commandStr)
            
        elif char in '\x1b':                # arrow key pressed
            null = getch()                  # waste a character
            direction = getch()             # grab the direction
            
            if direction in 'A':            # up arrow pressed
                # get the PREVIOUS command from your history (if there is one)
                # prints out 'up' then erases it (just to show something)
                # commandStr += u"\u2191"
                if movingIndex:
                    movingIndex -= 1 
                    commandStr = historyList[movingIndex]
                else:
                    if historyList:
                        commandStr = historyList[0]
                    else:
                        commandStr = ""

                print_cmd(commandStr)
                
            if direction in 'B':            # down arrow pressed
                # get the NEXT command from history (if there is one)
                # prints out 'down' then erases it (just to show something)
                # commandStr += u"\u2193"

                if movingIndex < len(historyList):
                    movingIndex += 1
                    if movingIndex < len(historyList):
                        commandStr = historyList[movingIndex]
                    else:
                        commandStr = ""
                else:
                    commandStr = ""

                # print_cmd(commandStr)
                       
            if direction in 'C':            # right arrow pressed  

                    commandStr = commandStr + "\x1b[C"
                    # print_cmd(commandStr)
                   
            if direction in 'D':            # left arrow pressed
                    commandStr = commandStr + "\x1b[D"
                    # print_cmd(commandStr)
                                  
        elif char in '\r':                  # return pressed 
            
            # If commandStr is empty, skip this iteration
            # commandStr = commandStr.lstrip()
            
            if not commandStr:
                print_cmd("\n")
                continue
            
            historyList.append(commandStr)
            movingIndex += 1

            commandList:list[ShellCommand] = parseCommand(commandStr)

            for i in range(0, len(commandList)):
                result:str = ""
                try:
                    if commandList[i].name.startswith("!"):
                        try:
                            index:int = int(commandList[i].name.removeprefix("!"))
                            commandStr = historyList[index-1]
                            break
                        except(ValueError, IndexError):
                            result = f"{commandStr}\n{commandList[i].name}: event not found\n"
                            print_cmd(result)
                            commandStr = ""
                            break
                    if commandList[i].name == "history":
                        result = history(historyList, flags=commandList[i].flags, params=commandList[i].params)

                        if not historyList:
                            movingIndex = 0
                    elif callable(getattr(cmd_pkg, commandList[i].name, None)):
                        commandFunc = getattr(cmd_pkg, commandList[i].name)

                        if commandList[i].fileIn:
                            with open(commandList[i].infile) as infile:
                                commandList[i].params.append(infile.read())

                        result = commandFunc(flags=commandList[i].flags, \
                                params=commandList[i].params, \
                                stdin= commandList[i].stdin, \
                                stdout=commandList[i].stdout)
                    else:
                        result = f"{commandStr}\n{commandList[i].name}: command not found\n"
                        print_cmd(result)
                        commandStr = ""
                        break
                except(SystemExit) as e:
                    with open(historyFileName, "w") as historyFile:
                        historyFile.write('\n'.join(historyList))
                    print_cmd(f"{commandStr}\n")
                    cmd_pkg.exit()
                # If next command recieves params from current command output, store output
                if i + 1 < len(commandList):
                    commandList[i+1].params.append(result)
                    result = ""
                elif commandList[i].fileOut:
                    with open(commandList[i].outfile, "w") as outfile:
                        outfile.write(result)
                        result = ""
                elif commandList[i].fileAppend:
                    with open(commandList[i].outfile, "a") as outfile:
                        outfile.write(result)
                        result = ""
                # If last command
                if i == len(commandList) - 1:
                    print_cmd(f"{commandStr}\n{result}\n")
                    commandStr = ""
        else:
            commandStr += char                     # add typed character to our "cmd"
            # print_cmd(commandStr)                  # print the cmd out
            # commandStr = ""