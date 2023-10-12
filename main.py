import cmd_pkg
from cmd_pkg import fileSystem
from ParseCommand import parseCommand, ShellCommand

# DB Constants
DB_PATH: str = "filesystem.sqlite"
CSV_FILE: str = "fakeFileData.csv"
TABLE_NAME: str = "FileSystem"

# ANSI Escape Sequences for controlling text colors
RESET = "\033[0m"  # Reset text formatting and color
BOLD = "\033[1m"  # Bold text
GREEN = "\033[92m"  # Green text
YELLOW = "\033[93m"  # Yellow text
CYAN = "\033[36m"  # Blue text
PURPLE = "\033[35m"  # Purple text


def prompt() -> str:
    """
    Returns a linux-like prompt.
    """
    directory = CYAN + fileSystem.get_cwd() + RESET

    return f"{directory}{GREEN+BOLD}$: {RESET}"


if __name__ == "__main__":
    fileSystem.set_db_path(DB_PATH)
    fileSystem.set_table_name(TABLE_NAME)
    fileSystem.csv_to_table(CSV_FILE)

    while True: # Exits when `exit` is entered
        cmdStr = input(prompt())

        # Singular, "simple" command is parsed
        temp = parseCommand(cmdStr)

        if not temp:
            continue

        shellCmd:shellCmd = temp[0]
    
        if callable(getattr(cmd_pkg, shellCmd.name, None)):
            commandFunc = getattr(cmd_pkg, shellCmd.name)
            result = commandFunc(
                flags=shellCmd.flags,
                params=shellCmd.params,
                stdin=shellCmd.stdin,
                stdout=shellCmd.stdout,
            )
            print(result)
        else:
            print(f"{shellCmd.name}: command not found")
