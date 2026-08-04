# create_users.py
import sqlite3
import hashlib
import secrets
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('edr.db')  # Change path if needed: 'app/edr.db'
cursor = conn.cursor()

print("="*50)
print("Creating users and admins in edr.db")
print("="*50)

# 1. Create Admin User in users table (is_admin = 1)
cursor.execute('''
INSERT OR IGNORE INTO users (username, std_id, password, std_of, date_join, active, valid, is_admin)
VALUES (?, ?, ?, ?, ?, 1, 1, 1)
''', ('admin', 'ADMIN001', 'admin123', 'Administration', datetime.now().isoformat()))

# 2. Create Regular User in users table (is_admin = 0)
cursor.execute('''
INSERT OR IGNORE INTO users (username, std_id, password, std_of, date_join, active, valid, is_admin)
VALUES (?, ?, ?, ?, ?, 1, 1, 0)
''', ('user1', 'USER001', 'user123', 'Computer Science', datetime.now().isoformat()))

# 3. Create Admin in admins table
cursor.execute('''
INSERT OR IGNORE INTO admins (name, permission, password)
VALUES (?, ?, ?)
''', ('superadmin', 'superadmin', 'admin123'))

# 4. Create more regular users
users = [
    ('john', 'STD001', 'user123', 'Math'),
    ('jane', 'STD002', 'user123', 'Physics'),
    ('bob', 'STD003', 'user123', 'Chemistry'),
]

for username, std_id, password, department in users:
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, std_id, password, std_of, date_join, active, valid, is_admin)
    VALUES (?, ?, ?, ?, ?, 1, 1, 0)
    ''', (username, std_id, password, department, datetime.now().isoformat()))

# Save changes
conn.commit()

# Show what was created
print("\n✅ Users created in 'users' table:")
cursor.execute("SELECT id, username, std_id, is_admin FROM users")
for row in cursor.fetchall():
    admin_status = " (Admin)" if row[3] else ""
    print(f"  ID: {row[0]}, Username: {row[1]}, Student ID: {row[2]}{admin_status}")

print("\n✅ Admins created in 'admins' table:")
cursor.execute("SELECT id, name, permission FROM admins")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Name: {row[1]}, Permission: {row[2]}")

# Close connection
conn.close()

print("\n" + "="*50)
print("🔐 LOGIN CREDENTIALS")
print("="*50)
print("\nFor /api/login endpoint (users table):")
print("  Username: admin, Password: admin123 (Admin)")
print("  Username: user1, Password: user123 (Regular)")
print("  Username: john, Password: user123 (Regular)")
print("  Username: jane, Password: user123 (Regular)")
print("  Username: bob, Password: user123 (Regular)")
print("\nFor /api/admin/login endpoint (admins table):")
print("  Name: superadmin, Password: admin123")
print("\n💡 Note: In production, passwords should be hashed with bcrypt!")