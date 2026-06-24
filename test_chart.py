import openpyxl
from openpyxl.chart import BarChart, Reference
from datetime import datetime, timedelta

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "test"
ws.append(["Дата", "Смена", "План (Листы)", "Факт (Листы)", "План (Тонны)", "Факт (Тонны)"])

sd = datetime.strptime("2026-06-10", "%Y-%m-%d").date()
row_idx = 2
for i in range(14):
    d_str = str(sd + timedelta(days=i))
    ws.append([d_str, "День", 2700, 1000, 50.0, 20.0])
    ws.append([d_str, "Ночь", 3300, 1200, 60.0, 25.0])
    row_idx += 2

chart_sheets = BarChart()
chart_sheets.type = "col"
chart_sheets.style = 10
chart_sheets.title = "Выработка (Листы)"
chart_sheets.y_axis.title = 'Количество (Листы)'
chart_sheets.x_axis.title = 'Дата / Смена'

data_sheets = Reference(ws, min_col=3, min_row=1, max_row=row_idx-1, max_col=4)
cats = Reference(ws, min_col=1, min_row=2, max_row=row_idx-1, max_col=2)

chart_sheets.add_data(data_sheets, titles_from_data=True)
chart_sheets.set_categories(cats)
chart_sheets.shape = 4
chart_sheets.width = 20

ws.add_chart(chart_sheets, "H2")
wb.save("test_chart.xlsx")
print("Chart created successfully")
