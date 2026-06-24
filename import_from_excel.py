import sqlite3
import openpyxl
from datetime import datetime

conn = sqlite3.connect('tectum.db')
cur = conn.cursor()

# Clear old fake data
cur.execute('DELETE FROM lfm_reports')
cur.execute('DELETE FROM downtimes')
cur.execute('DELETE FROM batches')
cur.execute('DELETE FROM shifts')
conn.commit()

# Read from Excel
wb = openpyxl.load_workbook("monthly_plan_board.xlsx", data_only=True)
ws = wb.active

shift_cache = {}

for row in ws.iter_rows(min_row=2, values_only=True):
    date_str, shift_type, master, shift_num, plan, fact = row
    if not date_str:
        continue
    
    # Check if fact is None, treat as 0
    fact = fact if fact is not None else 0
    
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
    # Insert shift
    cur.execute('''
        INSERT INTO shifts (date, shift_name, line, master_name, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (date_obj, shift_type, "Линия 2", master, "closed"))
    shift_id = cur.lastrowid
    
    # If there is a sanitary day, insert downtime. Plan < 1000 indicates a sanitary day
    if plan and plan < 1000:
        cur.execute('''
            INSERT INTO downtimes (shift_id, category, duration, start_time, end_time, node, description, lost_tons, lost_tenge, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (shift_id, "Санитарный день", 540, "08:00", "17:00", "Вся линия", "Плановый санитарный день", 0, 0, "resolved"))
        
    # Insert LFM report
    if fact > 0:
        cur.execute('''
            INSERT INTO lfm_reports (shift_id, product_name, lfm_sheets, lfm_wind_resets)
            VALUES (?, ?, ?, ?)
        ''', (shift_id, "Шифер 8 волн", fact, 0))

conn.commit()
conn.close()
print("Data imported successfully!")
