import sqlite3

conn = sqlite3.connect("finance.db")
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
rows = cur.fetchall()
print("TABLES:")
for name, sql in rows:
    print("-", name)
print("\nSCHEMA FOR income/expense if present:")
for tbl in ("income", "expense"):
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
    r = cur.fetchone()
    print(tbl, "=>", r[0] if r else None)

conn.close()

