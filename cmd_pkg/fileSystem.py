import sqlite3, os, csv, errno, stat
from pypika import Table, Query, Field, Column, Order
from datetime import datetime


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
        return self.__str__()


_db_path: str = "fileSystem.sqlite"

_table_name: str = "FileSystem"

_columns_info: list[tuple[str, str]] = [
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

_cwd: str = "/"


def _throw_FileNotFoundErr(path: str):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def _throw_NotADirectoryErr(path: str):
    raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), path)


def _throw_IsADirectory(path: str):
    raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), path)


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
    global _db_path
    _db_path = path


def get_db_path() -> str:
    return _db_path


def set_table_name(table_name: str) -> None:
    global _table_name
    _table_name = table_name


def get_table_name() -> str:
    return _table_name

# NOTE: This should probably be removed, most stuff is dependent on column names...
# def set_columns_info(columns_info: list[tuple[str, str]]) -> None:
#     global _columns_info
#     _columns_info = columns_info


def get_columns_info() -> list[tuple[str, str]]:
    return _columns_info


def get_cwd() -> str:
    """
    Returns current working directory.
    """
    return _cwd


def set_cwd(path: str) -> None:
    """
    Changes the current working directory. Must be full path starting with "/".
    Raises FileNotFoundError if not file
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundErr(path)
    elif not is_dir(path):
        _throw_NotADirectoryErr(path)
    else:
        global _cwd
        _cwd = path


def create_table(
    table_name: str | None = None,
    columns_info: list[tuple[str, str]] | None = None,
) -> bool:
    """
    Create a new table with specified columns, if it does not already exist.

    Args:
        table_name (str): Name of the table.
        columns (list): List of column definitions.
    """

    table_name = table_name if table_name else _table_name
    columns_info = columns_info if columns_info else _columns_info

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    try:
        # Create a table with the given columns, if not already existing
        query: str = (
            Query.create_table(table_name)
            .columns(*columns_info)
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

    drop_table()
    create_table()

    with open(file_name) as file:
        data = csv.reader(file)

        for record in data:
            _insert_entry(Entry(record))


def _find_id(path: str) -> int:
    """
    Returns id of given path. Returns -1 if does not exist.
    Must be full path beginning with "/".
    """

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


# NOTE: This is does not validate data, it must be in the correct format.


def _insert_entry(record: tuple | Entry) -> None:
    """
    Insert an entry into the table of the fileSystem database.
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
        _throw_FileNotFoundErr(path)

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

    entry: Entry = stats(path)

    return entry.file_type == "directory"


def is_file(path: str) -> bool:
    """
    Checks if path is a directory.
    Returns True if exists and file_type is a file
    Returns False if does not exist or file_type is directory.
    """
    path = abs_path(path)
    entry: Entry = stats(path)

    return entry.file_type == "file"


def norm_path(path: str) -> str:
    """
    Returns normalizes path.
    I.e, processes '.', '..', etc.
    """
    return os.path.normpath(path)


# TODO: Implement


def list_dir(path: str) -> list[Entry]:
    """
    Returns all entries within a directory.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundErr(path)
    if not is_dir(path):
        _throw_NotADirectoryErr(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    entries: list[Entry] = []

    try:
        entry_id: int = _find_id(path)
        print(entry_id)
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


# TODO: Implement
def chmod(path: str, mode: int) -> None:
    """
    Changes the permissions on a file/directory given octal 3-digit number.
    """
    path = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundErr(path)

    conn: sqlite3.Connection = sqlite3.connect(_db_path)
    cursor: sqlite3.Cursor = conn.cursor()

    if is_dir(path):
        mode += 0o40000
    else:
        mode += 0o100000

    modeStr:str = stat.filemode(mode)    

    try:
        entry_id:int = _find_id(path)
        query:str = Query.update(_table_name).set(Field("permissions"), modeStr).where(Field("id") == entry_id).get_sql()
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# TODO: Implement


def copy_file(src: str, dest: str) -> None:
    pass


# TODO: Implement


def move(src: str, dest: str) -> None:
    pass


# TODO: Implement


def make_dir(path: str) -> None:
    pass


def remove(path: str) -> None:
    """
    Removes an file.
    """
    path: str = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundErr(path)
    elif not is_file(path):
        _throw_IsADirectory(path)

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


# TODO: Implement


def remove_tree(path: str) -> None:
    """
    Recursively deletes everything in a directory, then deletes the directory.
    """
    path: str = abs_path(path)

    if not path_exists(path):
        _throw_FileNotFoundErr(path)
    elif not is_dir(path):
        _throw_NotADirectoryErr(path)

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
    return norm_path(os.path.join(_cwd, path))


# Example usage:
if __name__ == "__main__":
    try:
        from rich import print
    except ImportError:
        pass

    # drop_table()
    csv_to_table("fakeFileData.csv")
    chmod("/home/angel", 0o777)
    print(stats("/home/angel"))
    chmod("home/angel/Fortnite.exe", 0o777)
    print(stats("home/angel/Fortnite.exe"))
