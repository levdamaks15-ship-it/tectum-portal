import openpyxl

wb = openpyxl.load_workbook("test_report.xlsx")
ws = wb.active
for row in ws.iter_rows(values_only=True):
    print(row)
