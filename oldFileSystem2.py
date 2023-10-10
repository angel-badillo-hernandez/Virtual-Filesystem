import sqlite3, os, csv
from pypika import Table, Query, Field, Column, Order
from datetime import datetime


class FileSystem:
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

    __db_path: str = "fileSystem.sqlite"

    __table_name: str = "FileSystem"

    __columns_info: list[tuple[str, str]] = [
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

    __cwd: str = "/"

    @staticmethod
    def path_split(path: str) -> list[str]:
        """
        Splits path on slashes (/) and returns sections
        as a list.
        """
        # Remove trailing / to produce correct result
        if path.endswith("/"):
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

    @staticmethod
    def set_db_path(path: str) -> None:
        FileSystem.__db_path = path

    @staticmethod
    def get_db_path() -> str:
        return FileSystem.__db_path

    @staticmethod
    def set_table_name(table_name: str) -> None:
        FileSystem.__table_name = table_name

    @staticmethod
    def get_table_name() -> str:
        return FileSystem.__table_name

    @staticmethod
    def set_columns_info(columns_info: list[tuple[str, str]]) -> None:
        FileSystem.__columns_info = columns_info

    @staticmethod
    def get_columns_info() -> list[tuple[str, str]]:
        return FileSystem.__columns_info

    @staticmethod
    def get_cwd() -> str:
        """
        Returns current working directory.
        """
        return FileSystem.__cwd

    @staticmethod
    def set_cwd(path: str) -> bool:
        """
        Changes the current working directory. Must be full path starting with "/".
        Returns True if successful, false otherwise.
        """
        isValidPath: bool = FileSystem.path_exists(path) and FileSystem.is_dir(path)

        if isValidPath:
            FileSystem.__cwd = path

        return isValidPath

    @staticmethod
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

        table_name = table_name if table_name else FileSystem.__table_name
        columns_info = columns_info if columns_info else FileSystem.__columns_info

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
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

    @staticmethod
    def drop_table(table_name: str | None = None) -> bool:
        """
        Drop a table by name, optional parameter deletes specified table.
        If table_name is not passed in, uses FileSystem.__table_name.

        Args:
            table_name (str | None): Name of the table to drop.
        """

        table_name = table_name if table_name else FileSystem.__table_name

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
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

    @staticmethod
    def csv_to_table(file_name: str, table_name: str | None = None) -> None:
        """
        Put data from CSV into database table.
        """

        table_name = table_name if table_name else FileSystem.__table_name

        FileSystem.drop_table()
        FileSystem.create_table()

        with open(file_name) as file:
            data = csv.reader(file)

            for record in data:
                FileSystem.insert_entry(FileSystem.Entry(record))

    @staticmethod
    def _find_id(path: str) -> int:
        """
        Returns id of given path. Returns -1 if does not exist.
        Must be full path beginning with "/".
        """

        parts: list[str] = FileSystem.path_split(path)
        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()
        curr_id: int = 0

        try:
            if not parts or parts[0] != "/":
                return -1

            for i in range(1, len(parts)):
                query: str = (
                    Query.from_(FileSystem.__table_name)
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

    @staticmethod
    def _next_id(self) -> int:
        """
        Returns next available ID.
        """

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()
        try:
            query: str = (
                Query.from_(FileSystem.__table_name)
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
    @staticmethod
    def insert_entry(record: tuple | Entry) -> None:
        """
        Insert an entry into the table of the fileSystem database.
        """

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()

        try:
            if isinstance(record, FileSystem.Entry):
                record = dict(record).values()

            query: str = Query.into(FileSystem.__table_name).insert(*record).get_sql()
            cursor.execute(query)
            conn.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    # NOTE: This removes an entire row in db with no regard if it is a file.
    @staticmethod
    def remove_entry(path: str) -> bool:
        """
        Removes an entry, if it exists. Returns True if removed,
        false otherwise.
        """
        if not FileSystem.path_exists(path):
            return False

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()

        try:
            entry_id: int = FileSystem._find_id(path)

            query: str = (
                Query.from_(FileSystem.__table_name)
                .delete()
                .where(Field("id") == entry_id)
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

    @staticmethod
    def path_exists(path: str) -> bool:
        """
        Returns true if path exists. Must be a full path beginning with "/"
        """

        parts: list[str] = FileSystem.path_split(path)
        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()
        curr_id: int = 0

        try:
            if not parts or parts[0] != "/":
                return False

            for i in range(1, len(parts)):
                query: str = (
                    Query.from_(FileSystem.__table_name)
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

    @staticmethod
    def stats(path: str) -> Entry:
        """
        Returns the information of an entry in the file system, if it exists.
        """

        entry: FileSystem.Entry = None
        entry_id: int = None

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()

        try:
            entry_id: int = FileSystem._find_id(path)

            query: str = (
                Query.from_(FileSystem.__table_name)
                .select("*")
                .where(Field("id") == entry_id)
                .get_sql()
            )

            cursor.execute(query)

            record: tuple = cursor.fetchone()
            entry = FileSystem.Entry(record)
            return entry

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    @staticmethod
    def is_dir(absolute_path: str) -> bool:
        """
        Checks if path is a directory.
        Returns True if exists and file_type is a directory.
        Returns False if does not exist or file_type is file.
        """
        entry: FileSystem.Entry = FileSystem.stats(absolute_path)

        return entry.file_type == "directory"

    @staticmethod
    def is_file(absolute_path: str) -> bool:
        """
        Checks if path is a directory.
        Returns True if exists and file_type is a file
        Returns False if does not exist or file_type is directory.
        """
        entry: FileSystem.Entry = FileSystem.stats(absolute_path)

        return entry.file_type == "file"

    @staticmethod
    def abs_path(path: str) -> str:
        """
        Returns absolute path, and normalizes path.
        I.e, processes '.', '..', etc.
        """
        return os.path.normpath(f"{FileSystem.get_cwd()}{path}")

    @staticmethod
    def norm_path(path: str) -> str:
        """
        Returns normalizes path.
        I.e, processes '.', '..', etc.
        """
        return os.path.normpath(path)

    # TODO: Implement
    @staticmethod
    def list_dir(absolute_path: str) -> list[Entry]:
        """
        Returns all entries within a directory.
        """

        conn: sqlite3.Connection = sqlite3.connect(FileSystem.__db_path)
        cursor: sqlite3.Cursor = conn.cursor()
        entries: list[FileSystem.Entry] = []

        try:
            pass
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

        return entries

    # TODO: Implement
    @staticmethod
    def chmod(absolute_path: str, mode: int) -> None:
        pass

    # TODO: Implement
    @staticmethod
    def copy_file(absolute_src: str, absolute_dest: str) -> None:
        pass

    # TODO: Implement
    @staticmethod
    def move(absolute_src: str, absolute_dest: str) -> None:
        pass

    # TODO: Implement
    @staticmethod
    def make_dir(absolute_path: str) -> None:
        pass

    # TODO: Implement
    @staticmethod
    def remove(absolute_path: str) -> None:
        pass

    # TODO: Implement
    @staticmethod
    def remove_tree(absolute_path: str) -> None:
        pass


# Example usage:
if __name__ == "__main__":
    FileSystem.csv_to_table("fakeFileData.csv")

    path = "/home/angel/"
    print(FileSystem.is_dir(path))

    print(FileSystem.set_cwd(path))

    print(FileSystem.get_cwd())

    entry = FileSystem.stats(path)
    print(tuple(entry))
