# -*- coding: utf-8 -*-
import os

def search_in_file(filepath):
    print(f"\n=== Searching in {filepath} ===")
    if not os.path.exists(filepath):
        print("File not found")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        line_s = line.strip()
        # Look for edit UI interactions, fetches, api calls, modals
        if any(kw in line_s for kw in ["fetch", "method:", "PUT", "DELETE", "edit", "update", "save", "delete", "post", "POST"]):
            if len(line_s) > 120:
                line_s = line_s[:120] + "..."
            print(f"Line {i+1}: {line_s}")

search_in_file("static/js/app.js")
search_in_file("static/js/admin.js")
