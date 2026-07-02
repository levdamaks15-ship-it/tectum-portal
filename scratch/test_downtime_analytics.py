import sys
import os
from datetime import date, datetime

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session

from main import get_analytics_data
from database import SessionLocal
import models

def test_analytics_integration():
    db: Session = SessionLocal()
    test_shift = None
    try:
        # 1. Create a dummy shift
        test_shift = models.Shift(
            date=date(2026, 7, 2),
            shift_name="Дневная смена тест",
            line="ЛФМ-1",
            status="open"
        )
        db.add(test_shift)
        db.commit()
        db.refresh(test_shift)
        
        # 2. Add downtimes to this shift
        # 2.1 Stopping equipment downtime
        dt1 = models.Downtime(
            shift_id=test_shift.id,
            start_time="08:00",
            end_time="09:00",
            duration=60,
            lost_tons=10.0,
            lost_tenge=10000.0,
            category="Механические",
            department="Формование",
            node="Вакуум - Коробка",
            description="Засорение",
            is_equipment_downtime=True,
            status="resolved"
        )
        # 2.2 Non-stopping equipment downtime
        dt2 = models.Downtime(
            shift_id=test_shift.id,
            start_time="10:00",
            end_time="10:30",
            duration=30,
            lost_tons=5.0,
            lost_tenge=5000.0,
            category="Технологические",
            department="Формование",
            node="Смеситель",
            description="Чистка лопастей",
            is_equipment_downtime=False,
            status="resolved"
        )
        db.add(dt1)
        db.add(dt2)
        db.commit()
        
        # 3. Call the controller function directly
        data = get_analytics_data(
            start_date="2026-07-01",
            end_date="2026-07-03",
            department="Формование",
            db=db
        )
        
        print("API Response:", data)
        
        # Check structure
        assert "kpis" in data
        assert "by_category" in data
        assert "bottlenecks" in data
        assert "trend" in data
        
        # Check KPI values
        assert data["kpis"]["with_stop"]["duration"] == 60
        assert data["kpis"]["with_stop"]["count"] == 1
        assert data["kpis"]["without_stop"]["duration"] == 30
        assert data["kpis"]["without_stop"]["count"] == 1
        
        # Check categories structure
        assert "Механические" in data["by_category"]
        assert "Технологические" in data["by_category"]
        assert data["by_category"]["Механические"]["with_stop"] == 60
        assert data["by_category"]["Технологические"]["without_stop"] == 30
        
        print("\n=== Integration test passed successfully! ===")
        
    except Exception as e:
        print("Test failed with error:", e)
        raise e
    finally:
        # Clean up
        if test_shift:
            db.query(models.Downtime).filter(models.Downtime.shift_id == test_shift.id).delete()
            db.delete(test_shift)
            db.commit()
        db.close()

if __name__ == "__main__":
    test_analytics_integration()
