import sqlite3
from pypika import Table, Query, Field, Column

class FileSystem:

    def __init__(self,db_name:str | None= None, table_name:str | None = None, columns_info:list[tuple[str,str]] = None) -> None:
        
        self.table_name:str = table_name if table_name else "FileSystem"
        self.db_name:str = db_name if db_name else "fileSystem.sqlite"
        self.columns_info:list[tuple[str,str]] = columns_info if columns_info else [
            ("id", "INTEGER PRIMARY KEY"), 
            ("pid", "INTEGER"),
            ("file_name", "TEXT"), 
            ("file_type", "TEXT"),
            ("file_size", "REAL"), 
            ("owner_name", "TEXT"),
            ("group_name", "REAL"), 
            ("modification_time", "TEXT"),
            ("content", "BLOB")
        ]

        self.cwd:str = "/"
        self.cwdid:str = 0
    
    def create_table(self, table_name:str | None = None, columns_info:list[tuple[str,str]] | None = None) -> bool:
        """
        Create a new table with specified columns, if it does not already exist.

        Args:
            table_name (str): Name of the table.
            columns (list): List of column definitions.
        """

        table_name = table_name if table_name else self.table_name
        columns_info = columns_info if columns_info else self.columns_info

        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()

        try:
            # Create a table with the given columns, if not already existing
            query:str = Query.create_table(table_name).columns(*columns_info).if_not_exists().get_sql()
            cursor.execute(query)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    def drop_table(self, table_name:str | None) -> bool:
        """
        Drop a table by name, optional parameter deletes specified table.
        If table_name is not passed in, uses self.table_name.

        Args:
            table_name (str | None): Name of the table to drop.
        """

        table_name = table_name if table_name else self.table_name

        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()

        try:
            # Create a table with the given columns
            query:str = Query.drop_table(table_name).if_exists().get_sql()
            cursor.execute(query)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    def __getFileId(self, path:str) -> int:
        """ Find a file id using current location + name
        """
        pass

# Example usage:
if __name__ == "__main__":
    fileSystem = FileSystem()
