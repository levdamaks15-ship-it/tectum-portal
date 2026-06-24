import openpyxl
from datetime import datetime
from database import SessionLocal
import models

# ---------------------------------------------------------
# ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:
# 1. Положите файл Excel (например, "рапорт_АЦИ 10.06.26..xlsx") в эту папку.
# 2. Укажите правильное имя файла в переменной FILE_NAME ниже.
# 3. Запустите скрипт через терминал: python import_aci_instruction.py
# ---------------------------------------------------------

FILE_NAME = "рапорт_АЦИ 10.06.26..xlsx"

def import_aci_excel():
    db = SessionLocal()
    try:
        # Пытаемся открыть файл
        try:
            wb = openpyxl.load_workbook(FILE_NAME, data_only=True)
            ws = wb.active
        except Exception as e:
            print(f"Ошибка при открытии файла {FILE_NAME}: {e}")
            return
            
        print(f"Файл {FILE_NAME} успешно открыт. Начинаем чтение данных...")
        
        # Предполагаем структуру:
        # Колонка A: Дата (или Дата в шапке)
        # Нам нужно найти строки с данными: 1 сорт, брак, линия (Хоргос/Шанхай)
        
        # Так как точная структура нового файла Excel пока неизвестна, 
        # этот скрипт служит шаблоном (каркасом), который вы можете дополнить.
        
        # --- ПРАВИЛО ЛИНИЙ ---
        # Хоргос = Линия 1
        # Шанхай = Линия 2
        
        # Пример логики (требует корректировки номеров колонок под реальный файл):
        for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if not row or not row[0]: continue
            
            # Допустим, колонка 0 - дата, колонка 1 - линия (хоргос/шанхай)
            # колонка 2 - тип смены (День/Ночь)
            # колонка X - 1 сорт, колонка Y - брак
            # Это псевдо-логика для демонстрации:
            
            date_val = row[0]
            if isinstance(date_val, datetime):
                # date = date_val.date()
                pass
            
            line_val = str(row[1]).strip().lower() if len(row) > 1 and row[1] else ""
            db_line = "Линия 1" if "хоргос" in line_val else "Линия 2" if "шанхай" in line_val else None
            
            # if db_line and date:
            #     Найти смену:
            #     shift = db.query(models.Shift).filter_by(date=date, line=db_line, shift_name=shift_name).first()
            #     if shift:
            #         rep = db.query(models.LFMReport).filter_by(shift_id=shift.id).first()
            #         if rep:
            #             rep.formed_1st_grade = int(row[X])
            #             rep.formed_defect = int(row[Y])
            #             db.commit()
            
        print("Инструкция: Скрипт настроен. Как только у вас будет точная таблица, раскомментируйте логику и укажите номера колонок.")
        
    finally:
        db.close()

if __name__ == "__main__":
    import_aci_excel()
