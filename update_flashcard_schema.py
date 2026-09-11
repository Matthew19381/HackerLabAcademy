import sqlite3
import os

def table_has_column(cursor, table_name, column_name):
    """Check if a table has a given column."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_if_not_exists(cursor, table_name, column_name, column_def):
    """Add a column to a table if it doesn't exist."""
    if not table_has_column(cursor, table_name, column_name):
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            print(f"Added column {column_name} to {table_name}")
        except sqlite3.Error as e:
            print(f"Error adding column {column_name}: {e}")
    else:
        print(f"Column {column_name} already exists in {table_name}")

def main():
    db_path = '/c/GoogleDriveSync/Projekty/HackerLabAcademy/backend/HackerLabAcademy.db'
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure we are working with the flashcards table
        table_name = 'flashcards'

        # Define the columns we want to add (from the new model)
        columns_to_add = [
            ('stability', 'REAL'),
            ('difficulty', 'REAL'),
            ('state', 'INTEGER DEFAULT 1'),
            ('step', 'INTEGER'),
            ('last_review', 'DATETIME'),
            ('card_id', 'BIGINT'),
        ]

        for column_name, column_def in columns_to_add:
            add_column_if_not_exists(cursor, table_name, column_name, column_def)

        # Commit the changes
        conn.commit()
        print("Schema update completed.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()