import sqlite3
import os
#from pypika import Table, Query, Field, Column, Order
from pypika import *
import csv
from types import SimpleNamespace
from datetime import datetime

def path_split(path:str)-> list[str]:
        
        head, tail = os.path.split(path)
        parts:list[str] = []
        
        while True:
            path, dir = os.path.split(path)

            if dir != "":
                parts.append(dir)
            else:
                if path != "":
                    parts.append(path)
                break

        return parts[::-1]  # Reverse the list

class Entry:
    def __init__(self, record:tuple | None = None) -> None:
        """
        Creates instance of Entry. Creates Entry using tuple with
        corresponding values. If record is None, then creates Entry with
        all attributes set to None.
        """
        self.id:int = None
        self.pid:int = None
        self.file_name:str = None
        self.file_type:str = None
        self.file_size:float = None
        self.owner_name:str = None
        self.group_name:str = None
        self.permissions:str = None
        self.modification_time:str = None
        self.content:bytes = None

        if not record:
            return
        
        dictRecord:dict = dict(zip(dict(self).keys(), record))

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
        return str(dict(self))

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
            ("group_name", "TEXT"),
            ("permissions", "TEXT"), 
            ("modification_time", "TEXT"),
            ("content", "BLOB")
        ]

        self.cwd:str = "/"
    
    def get_cwd(self)-> str:
        return self.cwd

    def set_cwd(self, path:str) -> None:
        self.cwd = path

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

    def drop_table(self, table_name:str | None = None) -> bool:
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

    def csv_to_table(self, file_name:str, table_name:str | None=None) -> None:
        """
        Put data from CSV into database table.
        """

        table_name = table_name if table_name else self.table_name

        self.drop_table()
        self.create_table()

        with open(file_name) as file:
            data = csv.reader(file)

            for record in data:
                self.insert_entry(record)

    # TODO: Implement this
    def find_id(self, path:str) -> int:
        """ Find id of entry given the path
        """

        parts:list[str] = path_split(path)

        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()

        try:
            query:str = ""
            cursor.execute(query)
            conn.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    def next_id(self) -> int:
        """
        Returns next available ID.
        """
        
        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()
        try:
            query:str = Query.from_(self.table_name).select("id"
            ).orderby("id", order=Order.desc).limit(1).get_sql()

            cursor.execute(query)

            temp:tuple = cursor.fetchone()
            
            nextId:int | None = temp[0] + 1 if temp else 1
            return nextId
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    def insert_entry(self, record:tuple) -> None:
        """
        Insert a file into the table of the fileSystem database.
        """

        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()

        try:
            query:str = Query.into(self.table_name).insert(*record).get_sql()
            cursor.execute(query)
            conn.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    # TODO: Implement this
    def remove_entry(self, path:str) -> bool:
        """
        """
        pass

    # TODO: Implement this
    def path_exists(self, path:str) -> bool:
        """
        """
        pass

    # TODO: Implement this
    def path_stats(self, path:str, i:int) -> Entry | None:
        """
        Returns the information of an entry in the file system.
        """
        # If path does not exist, return None
        if self.path_exists(path):
            return None
        
        entry:Entry = None
        entry_id:int = None

        conn:sqlite3.Connection = sqlite3.connect(self.db_name)
        cursor:sqlite3.Cursor = conn.cursor()
        
        try:
            entry_id:int = self.find_id(path)

            query:str = Query.from_(self.table_name).select("*").where(
                Field("id") == entry_id).get_sql()
            
            cursor.execute(query)

            record:tuple = cursor.fetchone()
            if not record:
                return None
            else:
                entry = Entry(record)
                return entry

        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

# Example usage:
if __name__ == "__main__":
    fileSystem = FileSystem()

    fileSystem.csv_to_table("fakeFileData.csv")

    path = "/home/angel/Fortnite.exe"

    p = path_split(path)
    print(p)

    nextId = fileSystem.next_id()
    res = fileSystem.path_stats(path, 1)
    print(res)
    print(res.file_name)
