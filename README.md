# DormHub Manager

**DormHub Manager** is a professional university dormitory and cafeteria management system built with Django. It provides a comprehensive platform for both students and administrators to manage dormitory accommodations, meal orders, and maintenance requests efficiently.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🌐 Bilingual** | Full Persian / English support with RTL compatibility |
| **🌓 Dark & Light Themes** | Toggle between themes from the navigation bar |
| **🏠 Dual-Section Dormitory** | Separate sections for brothers and sisters |
| **🛏️ Room & Bed Management** | View roommates and bed numbers |
| **🎫 Ticket System** | Report room issues + admin response management |
| **🍽️ Weekly Meal Ordering** | Weekly menu + student balance tracking |
| **👤 Student & Admin Panels** | Separate dashboards for each role |
| **💰 Balance Management** | Admin can increase/decrease student balances |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/GoldenIsland00/DormHub_Manager.git
   cd DormHub_Manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install django django-crispy-forms crispy-bootstrap5 pillow
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create sample data** *(optional)*
   ```bash
   python create_sample_data.py
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser** and navigate to `http://127.0.0.1:8000`

---

## 🔑 Default Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Student (Male) | `ali_rezaei` | `student123` |
| Student (Female) | `sara_ahmadi` | `student123` |

---

## 📁 Project Structure

```
DormHub_Manager/
├── dorm_system/          # Main project settings
├── accounts/             # User authentication & dashboards
├── dormitory/            # Building, room & bed management
├── tickets/              # Ticket system & admin responses
├── cafeteria/            # Menu, meal orders & transactions
├── templates/            # HTML templates
├── static/               # Static assets (CSS, JS, images)
├── manage.py             # Django management script
├── create_sample_data.py # Sample data generator
└── db.sqlite3            # SQLite database
```

---

## 🧑‍💻 Usage Guide

1. **Log in** with an admin or student account
2. **Switch themes** using the sun/moon icon in the navbar
3. **Switch languages** from the language menu
4. **Students** can:
   - View their room and roommates
   - Submit and track maintenance tickets
   - Order meals from the weekly menu
   - Check their balance
5. **Admins** can manage all sections:
   - Add/edit/delete rooms and beds
   - Manage student balances
   - Respond to tickets
   - Configure weekly menus

---

## ⚠️ Important Notes

- The **brothers' section** only accepts male students, and the **sisters' section** only accepts female students
- **Meal orders** deduct from the student's balance automatically
- **Admins** can increase or decrease any student's balance

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django (Python) |
| Frontend | HTML, CSS, JavaScript (with RTL support) |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Images | Pillow |
| Database | SQLite (default) |

