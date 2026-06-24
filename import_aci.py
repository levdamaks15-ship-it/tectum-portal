import json
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import datetime

def import_data(file_path):
    db = SessionLocal()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} records from JSON.")
        
        # 1. Master mappings
        masters = {}
        for row in data:
            m_name = row.get("master", "").strip()
            if m_name and m_name not in masters:
                m = db.query(models.Master).filter_by(name=m_name).first()
                if not m:
                    m = models.Master(name=m_name, pin="0000", role="master")
                    db.add(m)
                    db.commit()
                    db.refresh(m)
                masters[m_name] = m.id
                
        # 2. Process shifts and batches
        shifts = {}
        batch_count = 0
        lfm_count = 0
        
        for row in data:
            s_date_str = row.get("date")
            s_name = str(row.get("shift", "")).strip()
            s_line = str(row.get("line", "")).strip()
            
            if not s_date_str: continue
            
            try:
                s_date = datetime.strptime(s_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            if "Д" in s_name.upper(): s_name = "День"
            elif "Н" in s_name.upper(): s_name = "Ночь"
            else: s_name = "День"
            
            if not s_line: 
                s_line = "Линия 1"
            else:
                if "хоргос" in s_line.lower():
                    s_line = "Линия 1"
                elif "шанхай" in s_line.lower():
                    s_line = "Линия 2"
                elif "1" in s_line:
                    s_line = "Линия 1"
                elif "2" in s_line:
                    s_line = "Линия 2"
            
            key = (s_date, s_name, s_line)
            if key not in shifts:
                master_name = row.get("master", "").strip()
                master_id = masters.get(master_name) if master_name else None
                
                shift = db.query(models.Shift).filter_by(date=s_date, shift_name=s_name, line=s_line).first()
                if not shift:
                    shift = models.Shift(
                        date=s_date,
                        shift_name=s_name,
                        line=s_line,
                        master_id=master_id,
                        status="closed"
                    )
                    db.add(shift)
                    db.commit()
                    db.refresh(shift)
                
                shifts[key] = {
                    "shift_id": shift.id,
                    "model": shift,
                    "data_filled": False
                }
                
            shift_info = shifts[key]
            shift_model = shift_info["model"]
            shift_id = shift_info["shift_id"]
            
            # Fill shift overall data only once per shift
            if not shift_info["data_filled"]:
                # The data in Excel is usually on the first row of the shift
                if row.get("receipt_cement_total") or row.get("batches_count"):
                    shift_model.receipt_cement = float(row.get("receipt_cement_total") or 0)
                    shift_model.zo_cement_silo1 = float(row.get("receipt_cement_silo1") or 0)
                    shift_model.zo_cement_silo2 = float(row.get("receipt_cement_silo2") or 0)
                    shift_model.zo_cement_silo3 = float(row.get("receipt_cement_silo3") or 0)
                    shift_model.zo_cement_silo4 = float(row.get("receipt_cement_silo4") or 0)
                    shift_model.zo_cement = (shift_model.zo_cement_silo1 + shift_model.zo_cement_silo2 + 
                                             shift_model.zo_cement_silo3 + shift_model.zo_cement_silo4)
                    
                    shift_model.zo_asb_drain = float(row.get("zo_asb_drain") or 0)
                    shift_model.zo_cem_drain = float(row.get("zo_cem_drain") or 0)
                    
                    shift_model.receipt_laprol = float(row.get("receipt_laprol") or 0)
                    shift_model.zo_laprol = float(row.get("zo_laprol") or 0)
                    
                    shift_model.receipt_cellulose = float(row.get("receipt_cellulose") or 0)
                    shift_model.zo_cellulose = float(row.get("zo_cellulose") or 0)
                    
                    shift_model.receipt_fiberglass = float(row.get("receipt_fiberglass") or 0)
                    shift_model.zo_fiberglass = float(row.get("zo_fiberglass") or 0)
                    
                    shift_model.receipt_crushed_slate = float(row.get("receipt_crushed_slate") or 0)
                    shift_model.zo_crushed_slate = float(row.get("zo_crushed_slate") or 0)
                    
                    shift_model.zo_asbozurit = float(row.get("zo_asbozurit") or 0)
                    shift_model.zo_batches = int(row.get("batches_count") or 0)
                    shift_model.zo_submitted = True
                    
                    db.commit()
                    shift_info["data_filled"] = True
            
            # Add Batch
            b_num = str(row.get("batch_number", "")).strip()
            product = str(row.get("product", "")).strip()
            
            if b_num and product:
                existing_batch = db.query(models.Batch).filter_by(shift_id=shift_id, batch_number=b_num).first()
                if not existing_batch:
                    # Сдано на склад это кондиция Разборщика/СКК. Для исторических данных будем считать, что это СКК кондиция.
                    transferred = int(row.get("transferred_to_warehouse") or 0)
                    
                    batch = models.Batch(
                        shift_id=shift_id,
                        batch_number=b_num,
                        product_name=product,
                        status="qcd_checked", # Historic batches are fully checked
                        stacked_stacks=0,
                        ds_condition=transferred,
                        qcd_condition=transferred,
                        qcd_first_grade=int(row.get("formed_1st_grade") or 0),
                        qcd_defect=int(row.get("formed_defect") or 0)
                    )
                    db.add(batch)
                    batch_count += 1
            
            # Add LFM Report
            if product and (row.get("lfm_sheets") or row.get("transferred_to_warehouse")):
                existing_lfm = db.query(models.LFMReport).filter_by(shift_id=shift_id, product_name=product).first()
                if not existing_lfm:
                    lfm = models.LFMReport(
                        shift_id=shift_id,
                        product_name=product,
                        lfm_sheets=int(row.get("lfm_sheets") or 0),
                        lfm_wind_resets=int(row.get("lfm_wind_resets") or 0),
                        formed_1st_grade=int(row.get("formed_1st_grade") or 0),
                        formed_defect=int(row.get("formed_defect") or 0),
                        transferred_to_warehouse=int(row.get("transferred_to_warehouse") or 0)
                    )
                    db.add(lfm)
                    lfm_count += 1
                    
        db.commit()
        print(f"Data migration completed. Created {batch_count} batches and {lfm_count} LFM reports.")
        
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()

if __name__ == "__main__":
    file_path = "aci_data.json"
    import_data(file_path)
