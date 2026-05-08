import sqlite3
import os
import json

db_path = r"c:\Users\Pavih\OneDrive\Desktop\project\lms_project\lms.db"
out_path = r"C:\Users\Pavih\.gemini\antigravity\brain\58c5ec31-443d-441a-855a-f1cf06bc8ed9\database_content.md"

if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall() if r[0] not in ('sqlite_sequence', 'alembic_version')]

md_lines = ["# Database Contents\n"]

for table in tables:
    md_lines.append(f"## Table: `{table}`\n")
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()
    
    md_lines.append(f"| {' | '.join(columns)} |")
    # Note: formatting correctly for markdown tables
    md_lines.append(f"|{'|'.join(['---'] * len(columns))}|")
    
    if not rows:
        md_lines.append(f"| {' | '.join(['*Empty*'] * len(columns))} |")
    else:
        for row in rows:
            row_str = [str(cell).replace('|', '\\|').replace('\n', ' ') if cell is not None else "NULL" for cell in row]
            md_lines.append(f"| {' | '.join(row_str)} |")
    md_lines.append("\n")

conn.close()

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Done")
