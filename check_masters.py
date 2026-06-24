import sqlite3

def check():
    conn = sqlite3.connect('tectum.db')
    c = conn.cursor()
    masters = c.execute("SELECT id, name, role FROM masters").fetchall()
    for m in masters:
        print(m)

if __name__ == "__main__":
    check()
