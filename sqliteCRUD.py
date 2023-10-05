# conn Class for Sqlite
from pypika import Table, Query, Field
import sqlite3
from prettytable import PrettyTable
# from types import SimpleNamespace # Allows convert dict to object with dict keys as attributes

class SQLiteCRUD:
    def __init__(self, db_path: str) -> None:
        """Initialize database connection and cursor."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __raw_results(self, results) -> list[str]:
        """Convert raw results to a list of table names."""
        table = []
        for row in results:
            table.append(row[0])
        return table

    def __formatted_results(self, results) -> PrettyTable:
        """Format results as a PrettyTable."""
        table = PrettyTable()
        table.field_names = [desc[0] for desc in self.cursor.description]
        table.add_rows(results)
        return table

    def create_table(self, table_name:str, columnsInfo:list[str]) -> None:
        """
        Params:
            table_name (str) - name of table
            columns (list) - ["id INTEGER PRIMARY KEY", "name TEXT", "created TEXT", "modified TEXT", "size REAL","type TEXT","owner TEXT","owner_group TEXT","permissions TEXT"]

        Create a new table with specified columns.

        Args:
            table_name (str): Name of the table.
            columns (list): List of column definitions.
        """
        try:
            # Create a table with the given columns
            create_table_query:str = (
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
            )
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print(f"Table '{table_name}' created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def drop_table(self, table_name:str) -> None:
        """
        Params:
            table_name (str) - name of table
            columns (list) - ["id INTEGER PRIMARY KEY", "name TEXT", "created TEXT", "modified TEXT", "size REAL","type TEXT","owner TEXT","owner_group TEXT","permissions TEXT"]
        Drop a table by name.

        Args:
            table_name (str): Name of the table to drop.
        """
        try:
            # Create a table with the given columns
            create_table_query = f"DROP TABLE IF EXISTS {table_name});"
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def show_tables(self, raw:bool=True) -> list[str]:
        """Show all tables in the database.

        Args:
            raw (bool): Whether to return raw results or formatted table.
        """
        table = Table("sqlite_master")
        query:str = Query.from_(table).select(table.name).where(table.type == "table").get_sql()
        self.cursor.execute(query)

        results = self.cursor.fetchall()

        if not raw:
            return self.__formatted_results(results)
        else:
            return self.__raw_results(results)

    def describe_table(self, table_name:str, raw:bool=False) -> PrettyTable | list[dict]:
        """Describe the structure of a table.

        Args:
            table_name (str): Name of the table.
            raw (bool): Whether to return raw data or a PrettyTable.
        """
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        results = self.cursor.fetchall()
        table = None

        if not raw:
            table = self.__formatted_results(results)

        else:
            table = []

            for column_info in results:
                column_name = column_info[1]
                data_type = column_info[2]
                is_nullable = "NULL" if column_info[3] == 0 else "NOT NULL"
                table.append(
                    {
                        "column_name": column_name,
                        "data_type": data_type,
                        "isnull": is_nullable,
                    }
                )
                # print(f"Column Name: {column_name}, Data Type: {data_type}, Nullable: {is_nullable}")

        return table

    def insert_data(self, table_name:str, data:tuple) -> None:
        """Insert data into a table.

        Args:
            table_name (str): Name of the table.
            data (tuple): Data to insert.
        """
        try:
            # Insert data into the table
            placeholders = ", ".join(["?"] * len(data))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders});"
            self.cursor.execute(insert_query, data)
            self.conn.commit()
            print("Data inserted successfully.")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def select(self, query:str)-> list[dict]:
        try:
            # Retrieve all data from the table
            results:list[dict[str]] = []

            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if result:
                #
                for row in result:
                   # Converts tuple to dict
                   results.append(dict(zip([desc[0] for desc in self.cursor.description], row)))
            else:
                print("No data found in the table.")
        except sqlite3.Error as e:
            print(f"Error reading data: {e}")
        return results

    def select_data(self, table_name:str) -> None:
        """Read data from a table.

        Args:
            table_name (str): Name of the table.
        """
        try:
            # Retrieve all data from the table
            select_query = f"SELECT * FROM {table_name};"
            self.cursor.execute(select_query)
            result = self.cursor.fetchall()
            if result:
                for row in result:
                    print(row)
            else:
                print("No data found in the table.")
        except sqlite3.Error as e:
            print(f"Error reading data: {e}")

    def update_data(
        self, table_name:str, column:str, new_value:str, condition_column:str, condition_value:str
    ) -> None:
        """Update data in a table based on a condition.

        Args:
            table_name (str): Name of the table.
            column (str): Column to update.
            new_value (str): New value to set.
            condition_column (str): Column to use in the WHERE clause.
            condition_value (str): Value to use in the WHERE clause.
        """
        try:
            # Update data in the table based on a conditionz
            query = Query.update(table_name).set(column, new_value).where(Field(condition_column) == condition_value).get_sql()
            print(query)
            update_query = (
                f"UPDATE {table_name} SET {column} = ? WHERE {condition_column} = ?;"
            )
            self.cursor.execute(update_query, (new_value, condition_value))
            self.conn.commit()
            print("Data updated successfully.")
        except sqlite3.Error as e:
            print(f"Error updating data: {e}")

    def delete_data(self, table_name:str, condition_column:str, condition_value:str) -> None:
        """Delete data from a table based on a condition.

        Args:
            table_name (str): Name of the table.
            condition_column (str): Column to use in the WHERE clause.
            condition_value (str): Value to use in the WHERE clause.
        """
        try:
            # Delete data from the table based on a condition
            delete_query = f"DELETE FROM {table_name} WHERE {condition_column} = ?;"
            self.cursor.execute(delete_query, (condition_value,))
            self.conn.commit()
            print("Data deleted successfully.")
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")

    def close_connection(self) -> None:
        """Close the database connection."""
        self.conn.close()
        print("Database connection closed.")

    def formatted_print(self, table_name:str) -> PrettyTable:
        """Print the contents of a table in a formatted manner.

        Args:
            table_name (str): Name of the table.
        """
        self.cursor.execute(f"SELECT * FROM {table_name};")
        table_info = self.cursor.fetchall()

        table_info_list = []

        table = PrettyTable()
        table.field_names = [desc[0] for desc in self.cursor.description]
        table.add_rows(table_info)

        return table

    def table_exists(self, table_name:str, db_path:str|None=None) -> bool:
        """Check if a table exists.

        Args:
            table_name (str): Name of the table.
            db_path (str, optional): Path to the database. Defaults to the initialized db_path.
        """
        different_conn = False
        if not db_path:
            db_path = self.db_path
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        else:
            different_conn = True
            conn = self.conn
            cursor = self.conn.cursor()

        try:
            # Query the sqlite_master table to check if the table exists
            table:Table = Table("sqlite_master")
            query:str = Query.from_(table).select(table.name).where(table.type == "table").where(table.name == table_name).get_sql()

            cursor.execute(query)
            result = cursor.fetchone()

            # If result is not None, the table exists
            return result is not None

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False

        finally:
            if different_conn:
                conn.close()

    def drop_table(self, table_name:str) -> bool:
        """Drop a table by its name.

        Args:
            table_name (str): Name of the table to drop.
        """
        try:
            # Drop the table if it exists
            query:str = Query.drop_table(table_name).get_sql()
            self.cursor.execute(query)

            # Commit the changes
            self.conn.commit()
            return True

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False


# Example usage:
if __name__ == "__main__":
    db_name = "students.sqlite"
    conn = SQLiteCRUD(db_name)

    # Define table schema
    table_name = "students"
    columns = ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"]

    # # Create table
    conn.create_table(table_name, columns)

    # Insert data
    data = ("1", "Alice", 25)
    conn.insert_data(table_name, data)

    data = ("2", "Bob", 23)
    conn.insert_data(table_name, data)

    data = ("3", "Charlie", 11)
    conn.insert_data(table_name, data)

    # Read data
    conn.select_data(table_name)

    # Update data
    conn.update_data(table_name, "age", 26, "name", "Alice")

    query = Query.from_(table_name).select("age", "name").where(Field("id") > 1).get_sql()
    print(query)
    res = conn.select(query)
    print(res)
    # Delete data
    # conn.delete_data(table_name, "name", "Alice")

    # Close the database connection

    #conn.drop_table("students")
    conn.close_connection()