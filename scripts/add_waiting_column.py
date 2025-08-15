import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check if column already exists
c.execute("PRAGMA table_info(users)")
columns = [col[1] for col in c.fetchall()]
if "awaiting" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN awaiting BOOLEAN DEFAULT 0")
    print("✅ 'awaiting' column added to users table.")
else:
    print("⚠️ 'awaiting' column already exists.")

conn.commit()
conn.close()
