import sqlite3

def upgrade():
    conn = sqlite3.connect("tectum.db")
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE monthly_plan_board ADD COLUMN first_grade INTEGER DEFAULT 0")
        print("Added first_grade")
    except Exception as e:
        print(e)
    try:
        cur.execute("ALTER TABLE monthly_plan_board ADD COLUMN defect INTEGER DEFAULT 0")
        print("Added defect")
    except Exception as e:
        print(e)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    upgrade()
