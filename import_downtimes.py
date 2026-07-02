import json
import os
import sys

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models

def import_downtimes():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Clean existing
    db.query(models.DowntimeDirectory).delete()
    db.commit()
    
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "База простоев.json")
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    entries = []
    
    # Category mapping from JSON codes to Database strings
    cat_map = {
        "М": "Механические",
        "Т": "Технологические",
        "Э": "Энергетические"
    }
    
    count = 0
    for entry in data.get("database", []):
        dept = entry.get("department")
        node = entry.get("node")
        subnode = entry.get("subnode")
        
        # Format node name (Node - Subnode) if subnode is provided
        if subnode:
            node_val = f"{node} - {subnode}"
        else:
            node_val = node
            
        for fault in entry.get("faults", []):
            reason = fault.get("reason")
            cat_code = fault.get("category")
            cat_val = cat_map.get(cat_code, "Механические")
            
            entries.append(models.DowntimeDirectory(
                department=dept,
                node=node_val,
                breakdown=reason,
                category=cat_val
            ))
            count += 1
            
    # Add special "Санитарный день" entry for LFM
    entries.append(models.DowntimeDirectory(
        department="ЛФМ",
        node="Санитарный день",
        breakdown="Комплексное обслуживание машины",
        category="Санитарный день"
    ))
    count += 1
    
    db.add_all(entries)
    db.commit()
    db.close()
    print(f"Successfully imported {count} downtime directory entries from JSON.")

if __name__ == "__main__":
    import_downtimes()
