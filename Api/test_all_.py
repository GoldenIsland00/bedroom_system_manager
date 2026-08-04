"""
ایجاد داده‌های تستی برای تمام جداول و فیلدهای سیستم خوابگاه
مشابه فایل test.py اما برای تمام موجودیت‌ها
"""

import sqlite3
import bcrypt
from datetime import datetime, timedelta
import random
import string

# اتصال به دیتابیس
conn = sqlite3.connect('edr.db')
cursor = conn.cursor()

print("="*70)
print("ایجاد داده‌های تستی برای تمام جداول سیستم خوابگاه")
print("="*70)

def generate_random_string(length=8):
    """تولید رشته تصادفی"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def hash_password(password):
    """هش کردن رمز عبور با bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ============================================================================
# 🗑️ مرحله 1: پاکسازی داده‌های قدیمی (اختیاری)
# ============================================================================
print("\n🗑️  پاکسازی داده‌های قدیمی...")

tables_to_clear = [
    'reports', 'eblaghieh', 'messages', 'room_users', 
    'rooms', 'foods', 'admins', 'users'
]

for table in tables_to_clear:
    try:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  ✅ جدول {table} پاک شد")
    except:
        print(f"  ⚠️  جدول {table} موجود نیست یا قابل پاک کردن نیست")

conn.commit()

# ============================================================================
# 👥 مرحله 2: ایجاد کاربران (جدول users)
# ============================================================================
print("\n" + "="*50)
print("👥 ایجاد کاربران در جدول users")
print("="*50)

users_data = [
    # (username, password, std_id, std_of, is_admin, active, valid, image)
    ('admin', 'admin123', 'ADMIN001', 'مدیریت سیستم', 1, 1, 1, 'admin.jpg'),
    ('user1', 'user123', 'STD1001', 'مهندسی کامپیوتر', 0, 1, 1, 'user1.jpg'),
    ('user2', 'user123', 'STD1002', 'مهندسی برق', 0, 1, 1, 'user2.jpg'),
    ('user3', 'user123', 'STD1003', 'مهندسی مکانیک', 0, 1, 1, 'user3.jpg'),
    ('user4', 'user123', 'STD1004', 'مهندسی عمران', 0, 1, 1, 'user4.jpg'),
    ('user5', 'user123', 'STD1005', 'علوم کامپیوتر', 0, 1, 1, 'user5.jpg'),
    ('user6', 'user123', 'STD1006', 'ریاضیات', 0, 0, 1, 'user6.jpg'),  # غیرفعال
    ('user7', 'user123', 'STD1007', 'فیزیک', 0, 1, 0, 'user7.jpg'),   # نامعتبر
]

user_ids = {}

for username, password, std_id, std_of, is_admin, active, valid, image in users_data:
    hashed_password = hash_password(password)
    
    cursor.execute('''
    INSERT INTO users (username, password, std_id, std_of, date_join, active, valid, image, is_admin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        username, hashed_password, std_id, std_of, 
        datetime.now().isoformat(), active, valid, image, is_admin
    ))
    
    # ذخیره ID کاربر
    user_id = cursor.lastrowid
    user_ids[username] = user_id
    print(f"  ✅ کاربر {username} (ID: {user_id}) - رشته: {std_of}")

conn.commit()

# ============================================================================
# 👑 مرحله 3: ایجاد ادمین‌ها (جدول admins)
# ============================================================================
print("\n" + "="*50)
print("👑 ایجاد ادمین‌ها در جدول admins")
print("="*50)

admins_data = [
    # (name, permission, password, img)
    ('superadmin', 'superadmin', 'admin123', 'superadmin.jpg'),
    ('admin1', 'admin', 'admin123', 'admin1.jpg'),
    ('admin2', 'moderator', 'admin123', 'admin2.jpg'),
]

for name, permission, password, img in admins_data:
    hashed_password = hash_password(password)
    
    cursor.execute('''
    INSERT INTO admins (name, permission, password, img)
    VALUES (?, ?, ?, ?)
    ''', (name, permission, hashed_password, img))
    
    print(f"  ✅ ادمین {name} - سطح دسترسی: {permission}")

conn.commit()

# ============================================================================
# 🍽️ مرحله 4: ایجاد غذاها (جدول foods)
# ============================================================================
print("\n" + "="*50)
print("🍽️  ایجاد غذاها در جدول foods")
print("="*50)

foods_data = [
    # (food_name, price, reserved, active, contain, user_id)
    ('قورمه سبزی', 75000, 0, 1, 'لوبیا، سبزی، گوشت، لیمو عمانی', user_ids['user1']),
    ('قیمه', 65000, 1, 1, 'لپه، سیب زمینی، گوشت چرخ کرده', user_ids['user2']),
    ('کباب کوبیده', 85000, 0, 1, 'گوشت چرخ کرده، پیاز، زعفران', user_ids['user3']),
    ('جوجه کباب', 90000, 1, 1, 'مرغ، ماست، زعفران، روغن', user_ids['user1']),
    ('میرزا قاسمی', 55000, 0, 1, 'بادمجان، گوجه، سیر، تخم مرغ', user_ids['user4']),
    ('کله پاچه', 120000, 0, 0, 'کله، پاچه، مغز', user_ids['user5']),  # غیرفعال
]

food_ids = []

for food_name, price, reserved, active, contain, user_id in foods_data:
    cursor.execute('''
    INSERT INTO foods (food_name, date, price, reserved, active, contain, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        food_name, 
        datetime.now().isoformat(), 
        price, 
        reserved, 
        active, 
        contain, 
        user_id
    ))
    
    food_id = cursor.lastrowid
    food_ids.append(food_id)
    
    status = "رزرو شده" if reserved else "آزاد"
    active_status = "فعال" if active else "غیرفعال"
    print(f"  ✅ غذا: {food_name} - قیمت: {price} - وضعیت: {status} - {active_status}")

conn.commit()

# ============================================================================
# 💬 مرحله 5: ایجاد پیام‌ها (جدول messages)
# ============================================================================
print("\n" + "="*50)
print("💬 ایجاد پیام‌ها در جدول messages")
print("="*50)

messages_data = [
    # (from_id, to_id, content, seen)
    (user_ids['user1'], user_ids['user2'], 'سلام! امتحان فردا ساعت چنده؟', 1),
    (user_ids['user2'], user_ids['user1'], 'ساعت 10 صبح در سالن اصلی', 1),
    (user_ids['admin'], user_ids['user3'], 'قبوض آب این ماه را پرداخت کنید', 0),
    (user_ids['user3'], user_ids['admin'], 'باشه حتما پرداخت می‌کنم', 0),
    (user_ids['user4'], user_ids['user5'], 'می‌تونی جزوه ریاضی را به من قرض بدی؟', 1),
    (user_ids['user5'], user_ids['user4'], 'حتما، فردا میارم برات', 0),
]

message_ids = []

for from_id, to_id, content, seen in messages_data:
    cursor.execute('''
    INSERT INTO messages (from_id, to_id, date, seen, content)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        from_id, 
        to_id, 
        (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(), 
        seen, 
        content
    ))
    
    message_id = cursor.lastrowid
    message_ids.append(message_id)
    
    seen_status = "دیده شده" if seen else "دیده نشده"
    print(f"  ✅ پیام از {from_id} به {to_id} - وضعیت: {seen_status}")

conn.commit()

# ============================================================================
# 📢 مرحله 6: ایجاد ابلاغیه‌ها (جدول eblaghieh)
# ============================================================================
print("\n" + "="*50)
print("📢 ایجاد ابلاغیه‌ها در جدول eblaghieh")
print("="*50)

eblaghieh_data = [
    # (to_id, is_res, topic, content)
    (user_ids['user1'], 0, 'اعلام نتایج', 'نتایج امتحانات نیمسال اول اعلام شد.'),
    (user_ids['user2'], 1, 'اخطار', 'قبض برق شما پرداخت نشده است.'),
    (user_ids['user3'], 0, 'اطلاعیه عمومی', 'جلسه عمومی خوابگاه روز پنجشنبه برگزار می‌شود.'),
    (user_ids['user4'], 1, 'اخطار انضباطی', 'شب گذشته پس از ساعت مقرر در خوابگاه بوده‌اید.'),
    (user_ids['user5'], 0, 'اطلاعیه غذایی', 'منوی هفته آینده غذاخوری اعلام شد.'),
]

for to_id, is_res, topic, content in eblaghieh_data:
    cursor.execute('''
    INSERT INTO eblaghieh (to_id, is_res, date, topic, content)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        to_id, 
        is_res, 
        datetime.now().isoformat(), 
        topic, 
        content
    ))
    
    eblaghieh_id = cursor.lastrowid
    
    res_status = "مهم" if is_res else "عادی"
    print(f"  ✅ ابلاغیه به کاربر {to_id} - موضوع: {topic} - سطح: {res_status}")

conn.commit()

# ============================================================================
# 🏠 مرحله 7: ایجاد اتاق‌ها (جدول rooms)
# ============================================================================
print("\n" + "="*50)
print("🏠 ایجاد اتاق‌ها در جدول rooms")
print("="*50)

rooms_data = [
    # (bed_num, options)
    (2, 'اینترنت, تلویزیون, سرویس بهداشتی'),
    (3, 'اینترنت, کولر, یخچال'),
    (4, 'اینترنت, آشپزخانه, ماشین لباسشویی'),
    (1, 'اینترنت, مطالعه'),
    (2, 'اینترنت, بالکن'),
]

room_ids = []

for bed_num, options in rooms_data:
    cursor.execute('''
    INSERT INTO rooms (bed_num, options)
    VALUES (?, ?)
    ''', (bed_num, options))
    
    room_id = cursor.lastrowid
    room_ids.append(room_id)
    
    print(f"  ✅ اتاق {room_id} - تعداد تخت: {bed_num} - امکانات: {options}")

conn.commit()

# ============================================================================
# 🔗 مرحله 8: اختصاص کاربران به اتاق‌ها (جدول room_users)
# ============================================================================
print("\n" + "="*50)
print("🔗 اختصاص کاربران به اتاق‌ها در جدول room_users")
print("="*50)

# کاربران و اتاق‌های تصادفی را به هم اختصاص می‌دهیم
room_assignments = [
    (room_ids[0], user_ids['user1']),
    (room_ids[0], user_ids['user2']),
    (room_ids[1], user_ids['user3']),
    (room_ids[1], user_ids['user4']),
    (room_ids[1], user_ids['user5']),
    (room_ids[2], user_ids['user1']),  # یک کاربر می‌تواند در چند اتاق باشد
    (room_ids[3], user_ids['admin']),
]

for room_id, user_id in room_assignments:
    cursor.execute('''
    INSERT OR IGNORE INTO room_users (room_id, user_id)
    VALUES (?, ?)
    ''', (room_id, user_id))
    
    print(f"  ✅ کاربر {user_id} به اتاق {room_id} اختصاص یافت")

conn.commit()

# ============================================================================
# 🚨 مرحله 9: ایجاد گزارش‌ها (جدول reports)
# ============================================================================
print("\n" + "="*50)
print("🚨 ایجاد گزارش‌ها در جدول reports")
print("="*50)

reports_data = [
    # (cont, room_id, user_id, seen, fixed)
    ('لوله آب در دستشویی نشتی دارد.', room_ids[0], user_ids['user1'], 1, 1),
    ('لامپ راهرو سوخته است.', room_ids[1], user_ids['user2'], 1, 0),
    ('کولر اتاق کار نمی‌کند.', room_ids[2], user_ids['user3'], 0, 0),
    ('درب کمد شکسته است.', room_ids[0], user_ids['user4'], 1, 1),
    ('شیر آب آشپزخانه چکه می‌کند.', room_ids[1], user_ids['user5'], 0, 0),
]

for cont, room_id, user_id, seen, fixed in reports_data:
    cursor.execute('''
    INSERT INTO reports (cont, date, seen, fixed, room_id, user_id)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        cont, 
        datetime.now().isoformat(), 
        seen, 
        fixed, 
        room_id, 
        user_id
    ))
    
    report_id = cursor.lastrowid
    
    seen_status = "دیده شده" if seen else "دیده نشده"
    fixed_status = "تعمیر شده" if fixed else "در انتظار تعمیر"
    print(f"  ✅ گزارش {report_id} - اتاق: {room_id} - وضعیت: {seen_status}/{fixed_status}")

conn.commit()

# ============================================================================
# 💰 مرحله 10: به‌روزرسانی وضعیت پرداخت کاربران
# ============================================================================
print("\n" + "="*50)
print("💰 به‌روزرسانی وضعیت پرداخت کاربران")
print("="*50)

# ابتدا مطمئن شویم فیلدهای پرداخت وجود دارند
try:
    # بررسی وجود فیلدها
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    payment_fields = ['has_paid', 'payment_date', 'payment_amount', 'next_payment_due', 'payment_notes']
    
    for field in payment_fields:
        if field not in columns:
            print(f"  ⚠️  فیلد {field} در جدول users وجود ندارد")
    
    # به‌روزرسانی وضعیت پرداخت برای برخی کاربران
    payment_updates = [
        (user_ids['user1'], 1, 500000, 'پرداخت کامل'),
        (user_ids['user2'], 1, 500000, 'پرداخت کامل'),
        (user_ids['user3'], 0, 0, 'پرداخت نشده'),
        (user_ids['user4'], 1, 250000, 'نیمه پرداخت'),
        (user_ids['user5'], 0, 0, 'پرداخت نشده'),
    ]
    
    for user_id, has_paid, amount, notes in payment_updates:
        try:
            cursor.execute('''
            UPDATE users 
            SET has_paid = ?, 
                payment_date = ?,
                payment_amount = ?,
                next_payment_due = ?,
                payment_notes = ?
            WHERE id = ?
            ''', (
                has_paid,
                datetime.now().isoformat() if has_paid else None,
                amount,
                (datetime.now() + timedelta(days=30)).isoformat() if has_paid else None,
                notes,
                user_id
            ))
            
            paid_status = "پرداخت شده" if has_paid else "پرداخت نشده"
            print(f"  ✅ کاربر {user_id} - وضعیت: {paid_status} - مبلغ: {amount}")
        except Exception as e:
            print(f"  ⚠️  خطا در به‌روزرسانی پرداخت کاربر {user_id}: {e}")
    
    conn.commit()
    
except Exception as e:
    print(f"  ⚠️  خطا در بخش پرداخت: {e}")

# ============================================================================
# 📊 مرحله 11: نمایش خلاصه داده‌های ایجاد شده
# ============================================================================
print("\n" + "="*70)
print("📊 خلاصه داده‌های ایجاد شده در دیتابیس")
print("="*70)

# شمارش رکوردهای هر جدول
tables = [
    ('users', '👤 کاربران'),
    ('admins', '👑 ادمین‌ها'),
    ('foods', '🍽️  غذاها'),
    ('messages', '💬 پیام‌ها'),
    ('eblaghieh', '📢 ابلاغیه‌ها'),
    ('rooms', '🏠 اتاق‌ها'),
    ('reports', '🚨 گزارش‌ها'),
    ('room_users', '🔗 تخصیص اتاق'),
]

for table, description in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{description}: {count} رکورد")
    except:
        print(f"{description}: جدول وجود ندارد")

# ============================================================================
# 🔐 مرحله 12: نمایش اطلاعات لاگین
# ============================================================================
print("\n" + "="*70)
print("🔐 اطلاعات ورود به سیستم")
print("="*70)

print("\n📌 برای endpoint /api/login (جدول users):")
print("  👤 ادمین: admin / admin123")
print("  👤 کاربران عادی:")
for username, user_id in user_ids.items():
    if username != 'admin':
        print(f"    - {username} / user123 (ID: {user_id})")

print("\n📌 برای endpoint /api/admin/login (جدول admins):")
print("  👑 ادمین سیستم: superadmin / admin123")
print("  👑 سایر ادمین‌ها: admin1 / admin123, admin2 / admin123")

print("\n📌 اطلاعات تستی دیگر:")
print(f"  🏠 تعداد اتاق‌ها: {len(room_ids)}")
print(f"  🍽️  تعداد غذاها: {len(food_ids)}")
print(f"  💬 تعداد پیام‌ها: {len(message_ids)}")

# ============================================================================
# 📝 مرحله 13: نمایش برخی داده‌های نمونه
# ============================================================================
print("\n" + "="*70)
print("📝 نمونه‌هایی از داده‌های ایجاد شده")
print("="*70)

print("\n🔹 برخی کاربران و اتاق‌های آنها:")
cursor.execute('''
SELECT u.id, u.username, u.std_of, GROUP_CONCAT(r.id) as room_ids
FROM users u
LEFT JOIN room_users ru ON u.id = ru.user_id
LEFT JOIN rooms r ON ru.room_id = r.id
WHERE u.active = 1
GROUP BY u.id
LIMIT 5
''')

for row in cursor.fetchall():
    room_info = f"اتاق‌ها: {row[3]}" if row[3] else "بدون اتاق"
    print(f"  👤 {row[1]} (ID: {row[0]}) - {row[2]} - {room_info}")

print("\n🔹 برخی غذاهای فعال:")
cursor.execute('''
SELECT f.food_name, f.price, u.username, f.reserved
FROM foods f
JOIN users u ON f.user_id = u.id
WHERE f.active = 1
LIMIT 3
''')

for row in cursor.fetchall():
    reserved_status = "🟢 آزاد" if row[3] == 0 else "🔴 رزرو شده"
    print(f"  🍽️  {row[0]} - {row[1]} تومان - توسط: {row[2]} - {reserved_status}")

print("\n🔹 برخی گزارش‌های باز:")
cursor.execute('''
SELECT r.id, r.cont, u.username, rm.id as room_id, r.fixed
FROM reports r
JOIN users u ON r.user_id = u.id
JOIN rooms rm ON r.room_id = rm.id
WHERE r.fixed = 0
LIMIT 3
''')

for row in cursor.fetchall():
    fixed_status = "✅ تعمیر شده" if row[4] == 1 else "⏳ در انتظار تعمیر"
    print(f"  🚨 گزارش {row[0]} - اتاق {row[3]} - توسط: {row[2]} - {fixed_status}")

# بستن اتصال
conn.close()

print("\n" + "="*70)
print("✅ ایجاد داده‌های تستی با موفقیت انجام شد!")
print("="*70)
print("\n🎯 اکنون می‌توانید از endpointهای زیر استفاده کنید:")
print("   🌐 API Documentation: http://localhost:8000/docs")
print("   📊 EDR Visualization: http://localhost:8000/edr")
print("   👤 تست لاگین: http://localhost:8000/api/login")
print("\n💡 نکته: تمام رمزهای عبور با bcrypt هش شده‌اند.")
print("   برای ورود از رمزهای 'admin123' یا 'user123' استفاده کنید.")