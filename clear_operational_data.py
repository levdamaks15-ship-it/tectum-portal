import sys
import os

# Add the project root to the path so we can import from database and models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def clear_operational_data():
    db = SessionLocal()
    try:
        # Delete data from operational tables
        deleted_batches = db.query(models.Batch).delete()
        deleted_lfm = db.query(models.LFMReport).delete()
        deleted_downtime = db.query(models.Downtime).delete()
        deleted_shifts = db.query(models.Shift).delete()
        
        db.commit()
        
        print(f"Очистка завершена успешно!")
        print(f"Удалено партий: {deleted_batches}")
        print(f"Удалено отчетов ЛФМ: {deleted_lfm}")
        print(f"Удалено простоев: {deleted_downtime}")
        print(f"Удалено смен: {deleted_shifts}")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при удалении данных: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    clear_operational_data()
