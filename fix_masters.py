import sqlite3

def fix_masters():
    conn = sqlite3.connect('tectum.db')
    c = conn.cursor()
    
    masters = c.execute("SELECT id, name FROM masters WHERE role='master'").fetchall()
    
    correct_names = {
        "Бекбосынов": "Бекбосынов Рауан",
        "Монаев": "Монаев Сарсен",
        "Султанулы": "Султанулы Сакен",
        "Дауылбай": "Дауылбай Мурат"
    }
    
    mapping = {k: [] for k in correct_names}
    
    for row in masters:
        m_id, name = row
        for base in correct_names:
            if base in name:
                mapping[base].append(m_id)
                break
                
    for base, ids in mapping.items():
        if not ids:
            continue
        primary_id = ids[0]
        full_name = correct_names[base]
        
        c.execute("UPDATE masters SET name = ? WHERE id = ?", (full_name, primary_id))
        
        for duplicate_id in ids[1:]:
            c.execute("UPDATE shifts SET master_id = ? WHERE master_id = ?", (primary_id, duplicate_id))
            c.execute("DELETE FROM masters WHERE id = ?", (duplicate_id,))
            
    conn.commit()
    conn.close()
    print("Fixed masters successfully.")

if __name__ == "__main__":
    fix_masters()
