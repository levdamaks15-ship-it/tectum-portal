import openpyxl
import json
from datetime import datetime, time

def parse_excel_to_json(file_path, output_json):
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb['рапорт']
        
        data = []
        # Пропускаем заголовки (первые 2 строки)
        current_date = datetime.now().date()
        for idx, row in enumerate(sheet.iter_rows(min_row=3, values_only=True)):
            if not row[0]: # Если даты нет, считаем, что данные закончились или строка пустая
                continue
                
            # Обработка даты
            date_val = row[0]
            if isinstance(date_val, datetime):
                if date_val.date() > current_date:
                    continue # Обрезаем по сегодняшнюю дату
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)
                
            # Пропускаем пустые строки, где нет мастера и продукта
            if not row[4] and not row[5]:
                continue
                
            shift_data = {
                "date": date_str,
                "batch_number": str(row[1]) if row[1] else "",
                "line": str(row[2]) if row[2] else "",
                "shift": str(row[3]) if row[3] else "",
                "master": str(row[4]) if row[4] else "",
                "product": str(row[5]) if row[5] else "",
                "batches_count": row[6] if row[6] else 0,
                
                # Формовка (ЛФМ)
                "lfm_sheets": row[7] if row[7] else 0,
                "lfm_tons": row[8] if row[8] else 0.0,
                "transferred_to_warehouse": row[9] if row[9] else 0,
                "formed_1st_grade": row[10] if row[10] else 0,
                "formed_defect": row[11] if row[11] else 0,
                "lfm_wind_resets": row[12] if row[12] else 0,
                
                # Сырье
                "receipt_cement_silo1": row[14] if row[14] else 0,
                "receipt_cement_silo2": row[15] if row[15] else 0,
                "receipt_cement_silo3": row[16] if row[16] else 0,
                "receipt_cement_silo4": row[17] if row[17] else 0,
                "receipt_cement_total": row[18] if row[18] else 0,
                
                "zo_asb_drain": row[19] if row[19] else 0,
                "zo_cem_drain": row[20] if row[20] else 0,
                
                "receipt_laprol": row[21] if row[21] else 0,
                "zo_laprol": row[22] if row[22] else 0,
                
                "receipt_cellulose": row[23] if row[23] else 0,
                "zo_cellulose": row[24] if row[24] else 0,
                
                "receipt_fiberglass": row[25] if row[25] else 0,
                "zo_fiberglass": row[26] if row[26] else 0,
                
                "receipt_crushed_slate": row[27] if row[27] else 0,
                "zo_crushed_slate": row[28] if row[28] else 0,
                
                "zo_asbozurit": row[29] if row[29] else 0,
                
                "mass_tons": row[49] if len(row) > 49 and row[49] else 0.0
            }
            data.append(shift_data)
            
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Успешно обработано {len(data)} записей (смен/партий). Сохранено в {output_json}")
        
    except Exception as e:
        print(f"Ошибка при обработке: {e}")

if __name__ == "__main__":
    file_path = "docs/excel/рапорт_АЦИ 10.06.26..xlsx"
    output_path = "aci_data.json"
    parse_excel_to_json(file_path, output_path)
