import sqlite3, os, csv, errno, stat
from pypika import Table, Query, Field, Column, Order
import datetime

_db_path: str = (
    "filesystem.sqlite"  # Global var for keeping track of path to database file
)

_table_name: str = "FileSystem"  # Global var for keeping track of path to table name

_columns_info: list[tuple[str, str]] = [  # Global var for keeping track of column names
    ("id", "INTEGER PRIMARY KEY"),
    ("pid", "INTEGER"),
    ("file_name", "TEXT"),
    ("file_type", "TEXT"),
    ("file_size", "REAL"),
    ("owner_name", "TEXT"),
    ("group_name", "TEXT"),
    ("permissions", "TEXT"),
    ("modification_time", "TEXT"),
    ("content", "BLOB"),
]

_cwd: str = "/"  # Global var for keeping track of current working directory


class Entry:
    def __init__(self, record: tuple | None = None) -> None:
        """
        Creates instance of Entry. Creates Entry using tuple with
        corresponding values. If record is None, then creates Entry with
        all attributes set to None.
        """
        self.id: int = None
        self.pid: int = None
        self.file_name: str = None
        self.file_type: str = None
        self.file_size: float = None
        self.owner_name: str = None
        self.group_name: str = None
        self.permissions: str = None
        self.modification_time: str = None
        self.content: bytes = None

        if not record:
            return

        dictRecord: dict = dict(zip(dict(self).keys(), record))

        for key, value in dictRecord.items():
            setattr(self, key, value)

    def __iter__(self):
        """
        Allows casting Entry to iterables such as list, tuple, and dict.
        """
        yield "id", self.id
        yield "pid", self.pid
        yield "file_name", self.file_name
        yield "file_type", self.file_type
        yield "file_size", self.file_size
        yield "owner_name", self.owner_name
        yield "group_name", self.group_name
        yield "permissions", self.permissions
        yield "modification_time", self.modification_time
        yield "content", self.content

    def __str__(self) -> str:
        """
        Cast Entry to str. Output matches that of a dict.
        """
        return str(dict(self))

    def __repr__(self) -> str:
        """
        Returns str representation of instance of Entry. Similar to dict.
        """
        return str(self)


def _throw_OSError(path: str, path2: str = None):
    """
    Raises OSError with given path(s).
    """
    raise OSError(errno.EINVAL, os.strerror(errno.EINVAL), path, None, path2)


def _throw_FileNotFoundError(path: str):
    """
    Raises FileNotFoundError with given path.
    """
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def _throw_NotADirectoryError(path: str):
    """
    Raises NotADirectoryError with given path.
    """
    raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), path)


def _throw_IsADirectoryError(path: str):
    """
    Raises IsADirectoryError with given path.
    """
    raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), path)


def _throw_FileExistsError(path: str):
    raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), path)


def path_split(path: str) -> list[str]:
    """
    Splits path on slashes (/) and returns sections
    as a list.
    """
    # Remove trailing / to produce correct result
    if len(path) > 1 and path.endswith("/"):
        path = path.removesuffix("/")

    # head, tail = os.path.split(path)
    parts: list[str] = []

    while True:
        path, dir = os.path.split(path)

        if dir != "":
            parts.append(dir)
        else:
            if path != "":
                parts.append(path)
            break

    return parts[::-1]  # Reverse the list


def set_db_path(path: str) -> None:
    """
    Set path to database file.
    """
    global _db_path
    _db_path = path


def get_db_path() -> str:
    """
    Get path to database file.
    """
    return _db_path


def set_table_name(table_name: str) -> None:
    """
    Set table name.
    """
    global _table_name
    _table_name = table_name


def get_table_name() -> str:
    """
    Get table name.
    """
    return _table_name


def get_columns_info() -> list[tuple[str, str]]:
    """
    Get columns info.
    """
    return _columns_info


def get_cwd() -> str:
    """
    Returns current working directory.
    """
    return _cwd


def set_cwd(path: str) -> None:
    """
    Changes the current working directory. Must be full path starting with "/".
    Raises FileNotFoundError if path does not exist. Raises NotADirectoryError
    if path is not a directory.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)
    elif not is_dir(path):
        _throw_NotADirectoryError(path)
    else:
        global _cwd
        _cwd = path


def create_table(
    table_name: str | None = None,
) -> bool:
    """
    Create a new table with specified columns, if it does not already exist.

    Args:
        table_name (str): Name of the table.
    """
    table_name = table_name if table_name else _table_name
    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        # Create a table with the given columns, if not already existing
        query: str = (
            Query.create_table(table_name)
            .columns(*_columns_info)
            .if_not_exists()
            .get_sql()
        )
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def drop_table(table_name: str | None = None) -> None:
    """
    Drop a table by name, optional parameter deletes specified table.
    If table_name is not passed in, uses __table_name.

    Args:
        table_name (str | None): Name of the table to drop.
    """

    table_name = table_name if table_name else _table_name

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        # Create a table with the given columns
        query: str = Query.drop_table(table_name).if_exists().get_sql()
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def csv_to_table(file_name: str, table_name: str | None = None) -> None:
    """
    Put data from CSV into database table.
    """

    table_name = table_name if table_name else _table_name

    drop_table(table_name)
    create_table(table_name)

    with open(file_name) as file:
        data = csv.reader(file)

        for record in data:
            _insert_entry(Entry(record))


def _find_id(path: str) -> int:
    """
    Returns id of given path. Returns -1 if does not exist.
    Must be full path beginning with "/".
    """
    path = abs_path(path)
    parts: list[str] = path_split(path)
    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    curr_id: int = 0

    try:
        if not parts or parts[0] != "/":
            return -1

        for i in range(1, len(parts)):
            query: str = (
                Query.from_(_table_name)
                .select("id")
                .where(Field("pid") == curr_id)
                .where(Field("file_name") == parts[i])
                .get_sql()
            )
            cursor.execute(query)
            curr_id = cursor.fetchone()

            curr_id = curr_id[0] if curr_id else -1

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    return curr_id


def _next_id() -> int:
    """
    Returns next available ID.
    """

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    try:
        query: str = (
            Query.from_(_table_name)
            .select("id")
            .orderby("id", order=Order.desc)
            .limit(1)
            .get_sql()
        )

        cursor.execute(query)

        temp: tuple = cursor.fetchone()

        nextId: int | None = temp[0] + 1 if temp else 1
        return nextId
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def _insert_entry(record: tuple | Entry) -> None:
    """
    Insert an entry into the table of the fileSystem database.
    Does not validate data. Must be correct format.
    """

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        if isinstance(record, Entry):
            record = dict(record).values()

        query: str = Query.into(_table_name).insert(*record).get_sql()
        cursor.execute(query)
        conn.commit()

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def path_exists(path: str) -> bool:
    """
    Returns true if path exists. Must be a full path beginning with "/"
    """
    path = abs_path(path)

    if path == "/":
        return True

    parts: list[str] = path_split(path)
    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    curr_id: int = 0

    try:
        if not parts or parts[0] != "/":
            return False

        for i in range(1, len(parts)):
            query: str = (
                Query.from_(_table_name)
                .select("id")
                .where(Field("pid") == curr_id)
                .where(Field("file_name") == parts[i])
                .get_sql()
            )
            cursor.execute(query)
            curr_id = cursor.fetchone()
            if not curr_id:
                return False

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    return True


def stats(path: str) -> Entry:
    """
    Returns the information of an entry in the file system.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)

    entry: Entry = None
    entry_id: int = None

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        entry_id: int = _find_id(path)
        query: str = (
            Query.from_(_table_name)
            .select("*")
            .where(Field("id") == entry_id)
            .get_sql()
        )

        cursor.execute(query)

        record: tuple = cursor.fetchone()
        entry = Entry(record)
        return entry

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def is_dir(path: str) -> bool:
    """
    Checks if path is a directory.
    Returns True if exists and file_type is a directory.
    Returns False if does not exist or file_type is file.
    """
    path = abs_path(path)

    if path == "/":
        return True

    parts: list[str] = path_split(path)
    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    curr_id: int = 0
    file_type: str = None

    try:
        if not parts or parts[0] != "/":
            return False

        for i in range(1, len(parts)):
            query: str = (
                Query.from_(_table_name)
                .select("id", "file_type")
                .where(Field("pid") == curr_id)
                .where(Field("file_name") == parts[i])
                .get_sql()
            )
            cursor.execute(query)
            row: tuple = cursor.fetchone()

            if not row:
                return False
            else:
                curr_id, file_type = row

        return True if file_type == "directory" else False

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    return True


def is_file(path: str) -> bool:
    """
    Checks if path is a file.
    Returns True if exists and file_type is a file
    Returns False if does not exist or file_type is directory.
    """
    path = abs_path(path)
    return not is_dir(path) and path_exists(path)


def norm_path(path: str) -> str:
    """
    Returns normalizes path.
    I.e, processes '.', '..', etc.
    """
    return os.path.normpath(path)


def list_dir(path: str) -> list[Entry]:
    """
    Returns all entries within a directory.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)
    if not is_dir(path):
        _throw_NotADirectoryError(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    entries: list[Entry] = []

    try:
        entry_id: int = _find_id(path)
        query: str = (
            Query.from_(_table_name)
            .select("*")
            .where(Field("pid") == entry_id)
            .get_sql()
        )
        cursor.execute(query)

        for record in cursor:
            entries.append(Entry(record))
        return entries
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    return entries


def chmod(path: str, mode: int) -> None:
    """
    Changes the permissions on a file/directory given octal 3-digit number.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    if is_dir(path):
        mode += 0o40000
    else:
        mode += 0o100000

    modeStr: str = stat.filemode(mode)

    try:
        entry_id: int = _find_id(path)
        query: str = (
            Query.update(_table_name)
            .set(Field("permissions"), modeStr)
            .where(Field("id") == entry_id)
            .get_sql()
        )
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def copy_file(src: str, dest: str) -> None:
    """
    Stuff
    """
    src = abs_path(src)
    dest = abs_path(dest)

    # If same path, just raise OSError
    if src == dest:
        _throw_OSError(src, dest)
    elif not path_exists(src):
        _throw_FileNotFoundError(src)
    elif not is_file(src):
        _throw_IsADirectoryError(src)

    # If dest is not directory, check if head of path os a directory
    if not is_dir(dest):
        parent, new_file_name = os.path.split(dest)

        # If head of path is not a directory or does not exist, raise FileNotFoundError
        if not path_exists(parent):
            _throw_FileNotFoundError(parent)
        elif not is_dir(parent):
            _throw_NotADirectoryError(parent)

        new_path: str = os.path.join(parent, new_file_name)
        # If path exists in target directory, raise FileExistsError
        if path_exists(new_path):
            _throw_FileExistsError(new_path)

    # If dest is a directory, use same name as filename from src
    else:
        parent = dest
        temp, new_file_name = os.path.split(src)

        # If same path, just raise OSError
        if src == os.path.join(dest, new_file_name):
            _throw_OSError(src, src)

        # File already exists in target directory, raise FileExistsError
        new_path: str = os.path.join(dest, new_file_name)
        if path_exists(new_path):
            _throw_FileExistsError(new_path)

    pid: int = _find_id(parent)
    new_file: Entry = stats(src)
    new_file.file_name = new_file_name
    new_file.pid = pid
    new_file.id = _next_id()
    new_file.modification_time = datetime.datetime.fromtimestamp(
        datetime.datetime.now().timestamp()
    ).isoformat(sep=" ", timespec="seconds")

    _insert_entry(new_file)


# TODO: Implement


def move(src: str, dest: str) -> None:
    """
    Stuff
    """
    src = abs_path(src)
    dest = abs_path(dest)

    # If same path, just raise OSError
    if src == dest:
        _throw_OSError(src, dest)
    elif not path_exists(src):
        _throw_FileNotFoundError(src)

    # If dest is not directory, check if head of path os a directory
    if not is_dir(dest):
        parent, new_file_name = os.path.split(dest)

        # If head of path is not a directory or does not exist, raise FileNotFoundError
        if not path_exists(parent):
            _throw_FileNotFoundError(parent)
        elif not is_dir(parent):
            _throw_NotADirectoryError(parent)

        new_path: str = os.path.join(parent, new_file_name)
        # If path exists in target directory, raise FileExistsError
        if path_exists(new_path):
            _throw_FileExistsError(new_path)

    # If dest is a directory, use same name as filename from src
    else:
        parent = dest
        temp, new_file_name = os.path.split(src)

        # If same path, just raise OSError
        if src == os.path.join(dest, new_file_name):
            _throw_OSError(src, src)

        # File already exists in target directory, raise FileExistsError
        new_path: str = os.path.join(dest, new_file_name)
        if path_exists(new_path):
            _throw_FileExistsError(new_path)

    pid: int = _find_id(parent)
    new_file: Entry = stats(src)
    new_file.file_name = new_file_name
    new_file.pid = pid
    new_file.modification_time = datetime.datetime.fromtimestamp(
        datetime.datetime.now().timestamp()
    ).isoformat(sep=" ", timespec="seconds")

    if is_file(src):
        remove(src)
        _insert_entry(new_file)
    else:
        dir_entries: list[Entry] = list_dir(src)

        for entry in dir_entries:
            entry.pid = new_file.id
            entry.modification_time = datetime.datetime.fromtimestamp(
                datetime.datetime.now().timestamp()
            ).isoformat(sep=" ", timespec="seconds")
        
        conn:sqlite3.Connection = sqlite3.connect(_db_path)
        cursor:sqlite3.Cursor = conn.cursor()

        try:
            for entry in dir_entries:
                query:str = Query.update(_table_name).set(Field("pid"), new_file.id).set(Field("modification_time"), entry.modification_time).where(Field("id") == entry.id).get_sql()
                cursor.execute(query)
                conn.commit()
            
            query:str = Query.update(_table_name).set(Field("pid"), pid).set(Field("file_name"), new_file.file_name).set(Field("modification_time"), new_file.modification_time).where(Field("id") == new_file.id).get_sql()
            cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

        
def make_dir(path: str) -> None:
    """
    Create directory if does not exist.
    """
    path = abs_path(path)

    if path_exists(path):
        _throw_FileExistsError(path)

    parent, dest = os.path.split(path)

    if not path_exists(parent):
        _throw_FileNotFoundError(parent)

    pid: int = _find_id(parent)
    new_dir: Entry = Entry()
    new_dir.id = _next_id()
    new_dir.pid = pid
    new_dir.file_name = dest
    new_dir.file_type = "directory"
    new_dir.file_size = 0
    new_dir.modification_time = datetime.datetime.fromtimestamp(
        datetime.datetime.now().timestamp()
    ).isoformat(sep=" ", timespec="seconds")
    new_dir.permissions = stat.filemode(0o40777)
    new_dir.owner_name = "user"
    new_dir.group_name = "user"
    new_dir.content = ""

    _insert_entry(new_dir)


def remove(path: str) -> None:
    """
    Removes an file.
    """
    path: str = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)
    elif not is_file(path):
        _throw_IsADirectoryError(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        entry_id: int = _find_id(path)

        query: str = (
            Query.from_(_table_name).delete().where(Field("id") == entry_id).get_sql()
        )
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def remove_dir(path: str) -> None:
    """
    Removes an empty directory.
    """
    path: str = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)
    elif not is_dir(path):
        _throw_IsADirectoryError(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        dir_entries: list[Entry] = list_dir(path)

        # If not empty, cannot delete directory
        if dir_entries:
            _throw_OSError(path)

        entry_id: int = _find_id(path)

        query: str = (
            Query.from_(_table_name).delete().where(Field("id") == entry_id).get_sql()
        )
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def remove_tree(path: str) -> None:
    """
    Recursively deletes everything in a directory, then deletes the directory.
    """
    path: str = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundError(path)
    elif not is_dir(path):
        _throw_NotADirectoryError(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        # Find id of top directory in tree
        rootEntry_id: int = _find_id(path)

        # Query to retrieve id,pid for all entries that have their pid
        # set to rootEntry_id.
        query: str = (
            Query.from_(_table_name)
            .select("id", "pid")
            .where(Field("pid") == rootEntry_id)
            .get_sql()
        )
        cursor.execute(query)
        idPairs: list[tuple] = cursor.fetchall()

        i: int = 0
        # Iterate over all id,pid pairs to retrieve all entries to delete
        while i < len(idPairs):
            query = (
                Query.from_(_table_name)
                .select("id", "pid")
                .where(Field("pid") == idPairs[i][0])
                .get_sql()
            )
            cursor.execute(query)
            temp = cursor.fetchall()
            idPairs.extend(temp)
            i += 1

        # Remove all entries belonging to the top directory in tree
        for id, pid in idPairs:
            query: str = (
                Query.from_(_table_name).delete().where(Field("id") == id).get_sql()
            )
            cursor.execute(query)

        # Remove top directory in tree
        query: str = (
            Query.from_(_table_name)
            .delete()
            .where(Field("id") == rootEntry_id)
            .get_sql()
        )
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def is_abs_path(path: str) -> bool:
    return True if path.startswith("/") else False


def is_relative_path(path: str) -> bool:
    return not is_abs_path(path)


def abs_path(path: str) -> bool:
    """
    Converts relative path to absolute path
    """
    return norm_path(os.path.join(_cwd, path))


# Example usage:
if __name__ == "__main__":
    csv_to_table("fakeFileData.csv")
    move("/home", "./sys/")
