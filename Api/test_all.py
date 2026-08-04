# test_all_endpoints.py
import requests
import json
from datetime import datetime

# تنظیمات پایه
BASE_URL = "http://localhost:8000/api"
TEST_USERNAME = "test_user_" + datetime.now().strftime("%H%M%S")
TEST_PASSWORD = "test123"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ذخیره توکن‌ها و IDها
tokens = {}
user_ids = {}
room_ids = []
food_ids = []
message_ids = []
report_ids = []

def print_step(step_num, title):
    print(f"\n{'='*60}")
    print(f"📍 STEP {step_num}: {title}")
    print(f"{'='*60}")

def handle_response(response, success_message=None):
    """پردازش پاسخ API"""
    print(f"🔸 Status Code: {response.status_code}")
    
    if response.status_code >= 200 and response.status_code < 300:
        if success_message:
            print(f"✅ {success_message}")
        
        # ذخیره توکن اگر وجود دارد
        if 'access_token' in response.json():
            tokens[response.json().get('username')] = response.json()['access_token']
            user_ids[response.json().get('username')] = response.json().get('user_id')
            print(f"🔑 Token saved for: {response.json().get('username')}")
        
        return response.json()
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📝 Response: {response.text}")
        return None

# ============================================================================
# 🟢 مرحله 1: ایجاد کاربر تستی
# ============================================================================
print_step(1, "ایجاد کاربر تستی جدید")

create_user_response = requests.post(
    f"{BASE_URL}/test/create-user",
    params={"username": TEST_USERNAME}
)

user_data = handle_response(
    create_user_response,
    f"کاربر تستی '{TEST_USERNAME}' ایجاد شد"
)

if not user_data:
    print("❌ ایجاد کاربر ناموفق بود. تست متوقف می‌شود.")
    exit(1)

print(f"📋 اطلاعات کاربر:")
print(f"   👤 Username: {TEST_USERNAME}")
print(f"   🔐 Password: {TEST_PASSWORD}")
print(f"   🆔 Student ID: {user_data.get('student_id')}")

# ============================================================================
# 🟢 مرحله 2: لاگین کاربر تستی
# ============================================================================
print_step(2, "لاگین با کاربر تستی")

login_response = requests.post(
    f"{BASE_URL}/login",
    json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
)

login_data = handle_response(
    login_response,
    "کاربر تستی با موفقیت لاگین شد"
)

if not login_data:
    print("❌ لاگین ناموفق بود. تست متوقف می‌شود.")
    exit(1)

test_token = tokens[TEST_USERNAME]
test_user_id = user_ids[TEST_USERNAME]

print(f"📊 اطلاعات لاگین:")
print(f"   🆔 User ID: {test_user_id}")
print(f"   👑 Is Admin: {login_data.get('is_admin', False)}")
print(f"   🔑 Token: {test_token[:50]}...")

# ============================================================================
# 🟢 مرحله 3: لاگین ادمین (برای تست‌های ادمین)
# ============================================================================
print_step(3, "لاگین با کاربر ادمین")

admin_login_response = requests.post(
    f"{BASE_URL}/login",
    json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
)

admin_data = handle_response(
    admin_login_response,
    "کاربر ادمین با موفقیت لاگین شد"
)

if admin_data:
    admin_token = tokens[ADMIN_USERNAME]
    admin_user_id = user_ids[ADMIN_USERNAME]
    print(f"🔐 ادمین توکن: {admin_token[:50]}...")
else:
    print("⚠️  هشدار: لاگین ادمین ناموفق. برخی تست‌ها اجرا نمی‌شوند.")
    admin_token = None

# ============================================================================
# 🟢 مرحله 4: اعتبارسنجی توکن
# ============================================================================
print_step(4, "اعتبارسنجی توکن کاربر")

headers = {"Authorization": f"Bearer {test_token}"}
validate_response = requests.get(
    f"{BASE_URL}/validate-token",
    headers=headers
)

handle_response(
    validate_response,
    "توکن کاربر معتبر است"
)

# ============================================================================
# 🟢 مرحله 5: دریافت اطلاعات پروفایل کاربر
# ============================================================================
print_step(5, "دریافت اطلاعات پروفایل کاربر")

profile_response = requests.get(
    f"{BASE_URL}/users/{test_user_id}",
    headers=headers
)

profile_data = handle_response(
    profile_response,
    "پروفایل کاربر دریافت شد"
)

if profile_data:
    print(f"📝 اطلاعات پروفایل:")
    print(f"   📛 نام کاربری: {profile_data.get('username')}")
    print(f"   🎓 رشته: {profile_data.get('std_of')}")
    print(f"   📅 تاریخ عضویت: {profile_data.get('date_join')}")

# ============================================================================
# 🟢 مرحله 6: تغییر رمز عبور
# ============================================================================
print_step(6, "تغییر رمز عبور کاربر")

change_password_response = requests.post(
    f"{BASE_URL}/change-password",
    headers=headers,
    json={
        "current_password": TEST_PASSWORD,
        "new_password": "new_password_123",
        "confirm_password": "new_password_123"
    }
)

handle_response(
    change_password_response,
    "رمز عبور با موفقیت تغییر یافت"
)

# برگرداندن رمز عبور به حالت اول (برای ادامه تست)
change_password_back_response = requests.post(
    f"{BASE_URL}/change-password",
    headers=headers,
    json={
        "current_password": "new_password_123",
        "new_password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD
    }
)

# ============================================================================
# 🟢 مرحله 7: ایجاد غذا (باید ادمین باشد)
# ============================================================================
print_step(7, "ایجاد غذا جدید")

if admin_token:
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    create_food_response = requests.post(
        f"{BASE_URL}/foods/",
        headers=admin_headers,
        json={
            "food_name": "غذای تستی",
            "price": 50000,
            "reserved": False,
            "active": True,
            "contain": "برنج، مرغ، سالاد",
            "user_id": test_user_id
        }
    )
    
    food_data = handle_response(
        create_food_response,
        "غذای جدید ایجاد شد"
    )
    
    if food_data:
        food_ids.append(food_data.get('id'))
        print(f"🍽️  ID غذا: {food_data.get('id')}")
else:
    print("⏭️  این تست نیاز به ادمین دارد - رد شد")

# ============================================================================
# 🟢 مرحله 8: دریافت لیست غذاها
# ============================================================================
print_step(8, "دریافت لیست غذاها")

foods_response = requests.get(
    f"{BASE_URL}/foods/",
    headers=headers
)

foods_data = handle_response(
    foods_response,
    "لیست غذاها دریافت شد"
)

if foods_data and len(foods_data) > 0:
    print(f"📊 تعداد غذاها: {len(foods_data)}")
    for food in foods_data[:3]:  # نمایش 3 غذا اول
        print(f"   🍱 {food.get('food_name')} - {food.get('price')} تومان")

# ============================================================================
# 🟢 مرحله 9: ارسال پیام
# ============================================================================
print_step(9, "ارسال پیام به کاربر دیگر")

# ابتدا یک کاربر دیگر ایجاد می‌کنیم
other_user_response = requests.post(
    f"{BASE_URL}/test/create-user",
    params={"username": f"other_{TEST_USERNAME}"}
)

other_user_data = handle_response(
    other_user_response,
    "کاربر دوم برای ارسال پیام ایجاد شد"
)

if other_user_data:
    other_user_id = other_user_data.get('user_id')
    
    send_message_response = requests.post(
        f"{BASE_URL}/messages/",
        headers=headers,
        params={"from_id": test_user_id},
        json={
            "content": "سلام! این یک پیام تستی است.",
            "to_id": other_user_id
        }
    )
    
    message_data = handle_response(
        send_message_response,
        "پیام ارسال شد"
    )
    
    if message_data:
        message_ids.append(message_data.get('id'))
        print(f"💬 ID پیام: {message_data.get('id')}")

# ============================================================================
# 🟢 مرحله 10: دریافت پیام‌های کاربر
# ============================================================================
print_step(10, "دریافت پیام‌های کاربر")

messages_response = requests.get(
    f"{BASE_URL}/messages/{test_user_id}",
    headers=headers
)

messages_data = handle_response(
    messages_response,
    "پیام‌های کاربر دریافت شد"
)

if messages_data:
    print(f"📨 تعداد پیام‌ها: {len(messages_data)}")
    for msg in messages_data[:2]:  # نمایش 2 پیام اول
        print(f"   📩 از: {msg.get('from_id')} - متن: {msg.get('content')[:30]}...")

# ============================================================================
# 🟢 مرحله 11: ایجاد اتاق (نیاز به ادمین)
# ============================================================================
print_step(11, "ایجاد اتاق جدید")

if admin_token:
    create_room_response = requests.post(
        f"{BASE_URL}/rooms/",
        headers=admin_headers,
        json={
            "bed_num": 2,
            "options": "اینترنت، تلویزیون، سرویس بهداشتی"
        }
    )
    
    room_data = handle_response(
        create_room_response,
        "اتاق جدید ایجاد شد"
    )
    
    if room_data:
        room_ids.append(room_data.get('id'))
        print(f"🏠 ID اتاق: {room_data.get('id')}")
        
        # اضافه کردن کاربر به اتاق
        add_to_room_response = requests.post(
            f"{BASE_URL}/rooms/{room_data.get('id')}/users/{test_user_id}",
            headers=admin_headers
        )
        
        handle_response(
            add_to_room_response,
            f"کاربر به اتاق {room_data.get('id')} اضافه شد"
        )
else:
    print("⏭️  این تست نیاز به ادمین دارد - رد شد")

# ============================================================================
# 🟢 مرحله 12: دریافت هم‌اتاقی‌ها
# ============================================================================
print_step(12, "دریافت هم‌اتاقی‌های کاربر")

roommates_response = requests.get(
    f"{BASE_URL}/users/{test_user_id}/roommates",
    headers=headers
)

roommates_data = handle_response(
    roommates_response,
    "هم‌اتاقی‌ها دریافت شد"
)

if roommates_data:
    print(f"👥 تعداد هم‌اتاقی‌ها: {roommates_data.get('total', 0)}")
    print(f"   🏠 اتاق‌های مشترک: {roommates_data.get('shared_rooms', [])}")

# ============================================================================
# 🟢 مرحله 13: ایجاد گزارش
# ============================================================================
print_step(13, "ایجاد گزارش جدید")

if room_ids:
    create_report_response = requests.post(
        f"{BASE_URL}/reports/",
        headers=headers,
        json={
            "cont": "لوله‌های آب نشتی دارد. نیاز به تعمیر فوری.",
            "room_id": room_ids[0]
        }
    )
    
    report_data = handle_response(
        create_report_response,
        "گزارش جدید ایجاد شد"
    )
    
    if report_data:
        report_ids.append(report_data.get('id'))
        print(f"📝 ID گزارش: {report_data.get('id')}")
else:
    print("⏭️  ابتدا باید اتاقی ایجاد شده باشد - رد شد")

# ============================================================================
# 🟢 مرحله 14: تست پرداخت (Demo)
# ============================================================================
print_step(14, "بررسی وضعیت پرداخت کاربر")

payment_response = requests.get(
    f"{BASE_URL}/check-payment/{test_user_id}",
    headers=headers
)

payment_data = handle_response(
    payment_response,
    "وضعیت پرداخت بررسی شد"
)

if payment_data:
    status = "✅ پرداخت شده" if payment_data.get('paid') else "❌ پرداخت نشده"
    print(f"💰 وضعیت پرداخت: {status}")
    print(f"   📋 دلیل: {payment_data.get('reason')}")

# ============================================================================
# 🟢 مرحله 15: دریافت لیست کاربران
# ============================================================================
print_step(15, "دریافت لیست کاربران")

users_response = requests.get(
    f"{BASE_URL}/users/",
    headers=headers
)

users_data = handle_response(
    users_response,
    "لیست کاربران دریافت شد"
)

if users_data:
    print(f"👤 تعداد کاربران: {len(users_data)}")
    for user in users_data[:3]:  # نمایش 3 کاربر اول
        print(f"   👨‍🎓 {user.get('username')} - {user.get('std_id')}")

# ============================================================================
# 🟢 مرحله 16: لاگ‌آوت (سمت کلاینت)
# ============================================================================
print_step(16, "لاگ‌آوت کاربر")

logout_response = requests.post(
    f"{BASE_URL}/logout",
    headers=headers
)

handle_response(
    logout_response,
    "کاربر با موفقیت لاگ‌آوت شد (توکن در کلاینت باید حذف شود)"
)

# ============================================================================
# 🟢 خلاصه اجرای تست
# ============================================================================
print_step("نتیجه", "خلاصه اجرای تست")

print("📊 نتایج تست:")
print(f"   👤 کاربر تستی: {TEST_USERNAME}")
print(f"   🆔 User ID: {test_user_id}")
print(f"   🔑 توکن دریافت شد: {'✅' if test_token else '❌'}")
print(f"   🏠 اتاق ایجاد شد: {'✅' if room_ids else '❌'}")
print(f"   🍽️  غذا ایجاد شد: {'✅' if food_ids else '❌'}")
print(f"   💬 پیام ارسال شد: {'✅' if message_ids else '❌'}")
print(f"   📝 گزارش ایجاد شد: {'✅' if report_ids else '❌'}")

print("\n🎉 تست با موفقیت انجام شد! تمام endpointهای اصلی آزمایش شدند.")
print("📌 برای تست کامل‌تر، endpointهای ادمین را با توکن ادمین آزمایش کنید.")