import json
import sqlite3
from datetime import datetime
from database import SessionLocal
from models import Master, Shift, LFMReport, ProductNorm

def update_schema():
    conn = sqlite3.connect('tectum.db')
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE shifts ADD COLUMN plan_sheets INTEGER DEFAULT 0")
    except Exception as e:
        print("plan_sheets already exists or error:", e)
        
    try:
        c.execute("ALTER TABLE shifts ADD COLUMN plan_tons FLOAT DEFAULT 0.0")
    except Exception as e:
        print("plan_tons already exists or error:", e)
    
    conn.commit()
    conn.close()

def seed_new_board():
    db = SessionLocal()
    with open('monthly_plan_board.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if there's already a product norm for 'Шифер 8 волн'
    norm = db.query(ProductNorm).filter(ProductNorm.product_name == "Шифер 8 волн").first()
    if not norm:
        norm = ProductNorm(product_name="Шифер 8 волн", weight_kg=18.2)
        db.add(norm)
        db.commit()
        db.refresh(norm)
        
    weight_kg = norm.weight_kg

    for row in data[1:]: # skip header
        if len(row) < 6:
            continue
        date_str, shift_type, master_name_raw, shift_num, plan, fact = row
        if not date_str:
            continue
            
        # Parse date from dd.mm.yyyy
        try:
            dt = datetime.strptime(date_str, "%d.%m.%Y").date()
        except Exception:
            continue
            
        # Map master names from Excel to DB names
        master_mapping = {
            "Султанулы С.": "Султанулы Сакен",
            "Дауылбай М.": "Дауылбай М.",
            "Монаев С.": "Монаев С.",
            "Бекбосынов Р.": "Бекбосынов Р."
        }
        mapped_name = master_mapping.get(master_name_raw, master_name_raw)
        
        master = db.query(Master).filter(Master.name == mapped_name).first()
        if not master:
            master = Master(name=mapped_name, role="master", pin="0000")
            db.add(master)
            db.commit()
            db.refresh(master)
            
        plan_sheets = 0
        if plan:
            try:
                plan_sheets = int(plan)
            except:
                pass
                
        plan_tons = (plan_sheets * weight_kg) / 1000.0
        
        # Check if shift exists
        shift = db.query(Shift).filter(
            Shift.date == dt,
            Shift.shift_name == shift_type,
            Shift.master_id == master.id
        ).first()
        
        if not shift:
            shift = Shift(
                date=dt,
                shift_name=shift_type,
                line="Линия 2",
                master_id=master.id,
                status="closed",
                plan_sheets=plan_sheets,
                plan_tons=plan_tons
            )
            db.add(shift)
            db.commit()
            db.refresh(shift)
        else:
            shift.plan_sheets = plan_sheets
            shift.plan_tons = plan_tons
            db.commit()
            
        # Update or add LFM report if fact is present
        if fact:
            try:
                fact_sheets = int(fact)
                rep = db.query(LFMReport).filter(LFMReport.shift_id == shift.id).first()
                if not rep:
                    rep = LFMReport(
                        shift_id=shift.id,
                        product_name="Шифер 8 волн",
                        lfm_sheets=fact_sheets,
                        lfm_wind_resets=0
                    )
                    db.add(rep)
                else:
                    rep.lfm_sheets = fact_sheets
                db.commit()
            except:
                pass

    print("Seed new board done!")
    db.close()

if __name__ == '__main__':
    update_schema()
    seed_new_board()
