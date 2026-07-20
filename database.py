import sqlite3

connection = sqlite3.connect("finance.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    source TEXT,
    amount REAL
)
""")

# If finance.db already exists without the `category` or `date` or `username` columns, migrate it.
cursor.execute("PRAGMA table_info(income)")
income_columns = {row[1] for row in cursor.fetchall()}
if "category" not in income_columns:
    cursor.execute("ALTER TABLE income ADD COLUMN category TEXT")
if "date" not in income_columns:
    cursor.execute("ALTER TABLE income ADD COLUMN date TEXT")
if "username" not in income_columns:
    cursor.execute("ALTER TABLE income ADD COLUMN username TEXT")


cursor.execute("""
 CREATE TABLE IF NOT EXISTS expense(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    expense TEXT,
     amount REAL
)
""")

# If finance.db already exists without the `date` or `username` columns in expense, migrate it.
cursor.execute("PRAGMA table_info(expense)")
expense_columns = {row[1] for row in cursor.fetchall()}
if "date" not in expense_columns:
    cursor.execute("ALTER TABLE expense ADD COLUMN date TEXT")
if "username" not in expense_columns:
    cursor.execute("ALTER TABLE expense ADD COLUMN username TEXT")

# Create users table before closing connection
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS budget(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL
    )
               """)
connection.commit()
connection.close()

print("Database Created Successfully!")


