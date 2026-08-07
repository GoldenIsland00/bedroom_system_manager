"""
Run after migrate:
python manage.py shell < create_sample_data.py
or: python create_sample_data.py (after setting DJANGO_SETTINGS_MODULE)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dorm_system.settings')
django.setup()

from accounts.models import User
from dormitory.models import Building, Room, Bed
from cafeteria.models import MealType, WeeklyMenu
from django.utils import timezone
from datetime import timedelta

# Admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@uni.ac.ir',
        password='admin123',
        first_name='مدیر',
        last_name='سیستم',
        role='admin',
    )
    print('Admin created: admin / admin123')

# Students
students_data = [
    ('ali_rezaei', 'علی', 'رضایی', 'male', '4001234567', 500000),
    ('reza_mohammadi', 'رضا', 'محمدی', 'male', '4001234568', 300000),
    ('hossein_karimi', 'حسین', 'کریمی', 'male', '4001234569', 400000),
    ('sara_ahmadi', 'سارا', 'احمدی', 'female', '4001234570', 600000),
    ('maryam_hosseini', 'مریم', 'حسینی', 'female', '4001234571', 250000),
    ('fateme_nouri', 'فاطمه', 'نوری', 'female', '4001234572', 350000),
]

for username, first, last, gender, sid, bal in students_data:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            password='student123',
            first_name=first,
            last_name=last,
            gender=gender,
            student_id=sid,
            role='student',
            balance=bal,
        )
print('Students created (password: student123)')

# Buildings
brothers, _ = Building.objects.get_or_create(
    name='خوابگاه برادران ۱',
    defaults={'section': 'brothers', 'floors': 4}
)
sisters, _ = Building.objects.get_or_create(
    name='خوابگاه خواهران ۱',
    defaults={'section': 'sisters', 'floors': 3}
)

# Rooms & Beds for brothers
for i in range(1, 5):
    room, created = Room.objects.get_or_create(
        building=brothers, number=f'10{i}',
        defaults={'floor': 1, 'capacity': 4}
    )
    if created:
        for b in range(1, 5):
            Bed.objects.create(room=room, bed_number=b)

# Rooms & Beds for sisters
for i in range(1, 4):
    room, created = Room.objects.get_or_create(
        building=sisters, number=f'20{i}',
        defaults={'floor': 1, 'capacity': 4}
    )
    if created:
        for b in range(1, 5):
            Bed.objects.create(room=room, bed_number=b)

# Assign some students
male_students = list(User.objects.filter(gender='male', role='student'))
female_students = list(User.objects.filter(gender='female', role='student'))
bro_beds = list(Bed.objects.filter(room__building=brothers, is_occupied=False)[:3])
sis_beds = list(Bed.objects.filter(room__building=sisters, is_occupied=False)[:3])

for student, bed in zip(male_students, bro_beds):
    bed.assign_student(student)
for student, bed in zip(female_students, sis_beds):
    bed.assign_student(student)
print('Beds assigned')

# Meal types
meals = [
    ('چلوکباب کوبیده', 'Kebab with Rice', 85000),
    ('قورمه سبزی', 'Ghormeh Sabzi', 75000),
    ('چلو مرغ', 'Chicken with Rice', 70000),
    ('عدس پلو', 'Adas Polo', 55000),
    ('صبحانه کامل', 'Full Breakfast', 35000),
    ('سوپ و سالاد', 'Soup & Salad', 40000),
]
for name_fa, name_en, price in meals:
    MealType.objects.get_or_create(name_fa=name_fa, defaults={'name_en': name_en, 'price': price})

# Weekly menu
today = timezone.now().date()
days_since_sat = (today.weekday() + 2) % 7
week_start = today - timedelta(days=days_since_sat)
meal_types = list(MealType.objects.all())

for day in range(7):
    for idx, mt in enumerate(MealType.MealTime.choices if hasattr(MealType, 'MealTime') else [('lunch','lunch'),('dinner','dinner')]):
        pass

from cafeteria.models import WeeklyMenu
meal_times = ['breakfast', 'lunch', 'dinner']
for day in range(7):
    for i, mt in enumerate(meal_times):
        if i < len(meal_types):
            WeeklyMenu.objects.get_or_create(
                week_start=week_start,
                day=day,
                meal_time=mt,
                defaults={'meal_type': meal_types[i % len(meal_types)], 'is_available': True}
            )
print('Sample data created successfully!')
print('Login: admin / admin123  or  ali_rezaei / student123')
