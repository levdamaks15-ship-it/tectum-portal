import sqlite3
conn = sqlite3.connect('tectum.db')
c = conn.cursor()
masters = c.execute("SELECT id, name FROM masters WHERE role='master'").fetchall()
for r in masters:
    print(f"ID: {r[0]}, Name: {r[1].encode('utf-8')}")
conn.close()
