import sqlite3

def merge():
    conn = sqlite3.connect('tectum.db')
    c = conn.cursor()
    masters = c.execute("SELECT id, name FROM masters WHERE role='master'").fetchall()
    
    id1 = None
    id2 = None
    
    for m in masters:
        if "Султанулы" in m[1]:
            id1 = m[0]
        if "Султанұлы" in m[1]:
            id2 = m[0]
            
    if id1 and id2 and id1 != id2:
        # Move shifts from id2 to id1
        c.execute("UPDATE shifts SET master_id = ? WHERE master_id = ?", (id1, id2))
        c.execute("DELETE FROM masters WHERE id = ?", (id2,))
        
        # update name to make it canonical
        c.execute("UPDATE masters SET name = 'Султанулы Сакен' WHERE id = ?", (id1,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    merge()
