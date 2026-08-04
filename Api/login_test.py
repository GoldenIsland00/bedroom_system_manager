# create_fresh_users.py
import sqlite3
import bcrypt
from datetime import datetime

conn = sqlite3.connect('edr.db')
cursor = conn.cursor()

# Clear old data (optional)
cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM admins")

# Create admin user with bcrypt hashed password
admin_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
cursor.execute('''
INSERT INTO users (username, password, std_id, std_of, is_admin, active, valid, date_join)
VALUES ('admin', ?, 'ADMIN001', 'Administration', 1, 1, 1, ?)
''', (admin_hash, datetime.now().isoformat()))

# Create regular user with bcrypt hashed password  
user_hash = bcrypt.hashpw(b'user123', bcrypt.gensalt()).decode('utf-8')
cursor.execute('''
INSERT INTO users (username, password, std_id, std_of, is_admin, active, valid, date_join)
VALUES ('user1', ?, 'USER001', 'Computer Science', 0, 1, 1, ?)
''', (user_hash, datetime.now().isoformat()))

# Create admin record with bcrypt hash
admin_record_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
cursor.execute('''
INSERT INTO admins (name, password, permission)
VALUES ('superadmin', ?, 'superadmin')
''', (admin_record_hash,))

conn.commit()
conn.close()

print("✅ Users created!")
print("\n🔐 LOGIN CREDENTIALS:")
print("For /api/login endpoint:")
print("  Username: admin")
print("  Password: admin123")
print("\n  Username: user1")  
print("  Password: user123")
print("\nFor /api/admin/login endpoint:")
print("  Name: superadmin")
print("  Password: admin123")