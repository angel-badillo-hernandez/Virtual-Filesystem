import sqlite3
#from pypika import Table, Query, Field, Column, Order
from pypika import *
import csv
from datetime import datetime

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
                self.insertEntry(record)

    def get_id(self, path:str) -> int:
        """ Find a file id using current location + name
        """

        pass
    
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

    def insertEntry(self, record:tuple) -> None:
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

        pass
  
    def removeEntry(self, path:str) -> bool:
        """
        """
        pass

    def pathExists(self, path:str) -> bool:
        """
        """
        
# Example usage:
if __name__ == "__main__":
    fileSystem = FileSystem()

    fileSystem.csv_to_table("fakeFileData.csv")
