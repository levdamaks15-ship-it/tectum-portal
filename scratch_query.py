import sqlite3
import sys

# Write with utf-8 to correctly handle Cyrillic characters
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('tectum.db')
cursor = conn.cursor()

shifts = cursor.execute('SELECT line, count(*) FROM shifts GROUP BY line').fetchall()
print("Shifts count by line:")
for row in shifts:
    print(f" - {row[0]}: {row[1]}")

lfm = cursor.execute('''
SELECT s.line, SUM(l.lfm_sheets)
FROM lfm_reports l
JOIN shifts s ON s.id = l.shift_id
GROUP BY s.line
''').fetchall()
print("\nLFM sheets by line:")
for row in lfm:
    print(f" - {row[0]}: {row[1]}")

