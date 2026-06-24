import sqlite3

def add_col():
    conn = sqlite3.connect("tectum.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE monthly_plan_board ADD COLUMN line VARCHAR")
        print("Added 'line' to monthly_plan_board.")
    except Exception as e:
        print(f"Error: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_col()
