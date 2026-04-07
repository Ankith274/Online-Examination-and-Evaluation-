"""
migrate_db.py – One-time database migration script.
Adds missing columns to existing tables and creates new tables.
Run with: .venv\Scripts\python migrate_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join('instance', 'exam_sys.db')

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# ── 1. audit_log: add 'details' column ───────────────────────────────────────
cur.execute('PRAGMA table_info(audit_log)')
audit_cols = [r[1] for r in cur.fetchall()]
print('audit_log existing columns:', audit_cols)

if 'details' not in audit_cols:
    cur.execute('ALTER TABLE audit_log ADD COLUMN details TEXT')
    print('  ✓ Added: details column to audit_log')
else:
    print('  – details column already present')

# ── 2. theory_paper table ─────────────────────────────────────────────────────
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='theory_paper'")
if not cur.fetchone():
    print('theory_paper table does not exist – creating via Flask db.create_all()...')
    conn.commit()
    conn.close()
    # Bootstrap via Flask app context so SQLAlchemy creates the table properly
    import sys
    sys.path.insert(0, '.')
    from app import app, db
    with app.app_context():
        db.create_all()
    print('  ✓ All missing tables created via db.create_all()')
else:
    print('  – theory_paper table already exists')
    conn.commit()
    conn.close()

print('\nMigration complete! Restart the Flask server.')
