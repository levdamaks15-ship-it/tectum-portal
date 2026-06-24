import openpyxl

wb = openpyxl.load_workbook("monthly_plan_board.xlsx")
ws = wb.active

total_plan = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[4]:
        total_plan += row[4]

print(f"Total Plan for June: {total_plan}")
