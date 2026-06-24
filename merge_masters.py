import sqlite3

def merge():
    conn = sqlite3.connect('tectum.db')
    c = conn.cursor()
    
    # 1. Fetch all masters
    masters = c.execute("SELECT id, name FROM masters WHERE role='master'").fetchall()
    
    # Target base names
    bases = ["Бекбосынов", "Монаев", "Дауылбай", "Султанулы"]
    primary_ids = {}
    
    for row in masters:
        m_id, name = row
        for base in bases:
            if base in name:
                if base not in primary_ids:
                    primary_ids[base] = m_id
                else:
                    # Duplicate found, update shifts and delete this master
                    target_id = primary_ids[base]
                    c.execute("UPDATE shifts SET master_id = ? WHERE master_id = ?", (target_id, m_id))
                    c.execute("DELETE FROM masters WHERE id = ?", (m_id,))
                break
                
    # Update names to be clean without initials if needed
    for base, m_id in primary_ids.items():
        c.execute("UPDATE masters SET name = ? WHERE id = ?", (base, m_id))
        
    conn.commit()
    conn.close()
    print("Merged successfully.")

if __name__ == "__main__":
    merge()
