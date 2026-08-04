from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from typing import List, Optional
import bcrypt
# Add these imports at the top of crud.py
from datetime import datetime
import bcrypt
from .auth import verify_password, get_password_hash


# Add these authentication functions to crud.py
def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate user by username or student ID and password
    """
    # Try to find user by username
    user = get_user_by_username(db, username)
    
    # If not found, try by student ID
    if not user:
        user = get_user_by_std_id(db, username)
    
    if not user:
        return False
    
    # Verify password (using bcrypt for compatibility)
    try:
        # First try bcrypt verification (for old passwords)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
    except:
        pass
    
    # Try passlib verification (for new passwords)
    if verify_password(password, user.password):
        return user
    
    return False

def update_user_last_login(db: Session, user_id: int):
    """Update user's last login timestamp"""
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
    return user

# Update create_user to use get_password_hash for consistency
def create_user(db: Session, user: schemas.UserCreate):
    # Use get_password_hash instead of bcrypt directly
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        std_id=user.std_id,
        password=hashed_password,
        std_of=user.std_of,
        date_join=datetime.utcnow(),
        active=True,
        valid=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Add function to verify admin credentials
def authenticate_admin(db: Session, name: str, password: str):
    """Authenticate admin by name and password"""
    admin = db.query(models.Admin).filter(models.Admin.name == name).first()
    
    if not admin:
        return False
    
    # Verify password
    try:
        if bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return admin
    except:
        pass
    
    if verify_password(password, admin.password):
        return admin
    
    return False

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_std_id(db: Session, std_id: str):
    return db.query(models.User).filter(models.User.std_id == std_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Use get_password_hash instead of bcrypt directly
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        std_id=user.std_id,
        password=hashed_password,
        std_of=user.std_of,
        date_join=datetime.utcnow(),
        active=True,
        valid=True,
        is_admin=getattr(user, 'is_admin', False)  
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Food CRUD operations
def create_food(db: Session, food: schemas.FoodCreate):
    db_food = models.Food(**food.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def get_foods(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Food).offset(skip).limit(limit).all()

def update_food(db: Session, food_id: int, food_data: dict):
    db_food = db.query(models.Food).filter(models.Food.id == food_id).first()
    if db_food:
        for key, value in food_data.items():
            setattr(db_food, key, value)
        db.commit()
        db.refresh(db_food)
    return db_food

def delete_food(db: Session, food_id: int):
    db_food = db.query(models.Food).filter(models.Food.id == food_id).first()
    if db_food:
        db.delete(db_food)
        db.commit()
    return db_food

# Message CRUD operations
def create_message(db: Session, message: schemas.MessageCreate, from_id: int):
    db_message = models.Message(**message.dict(), from_id=from_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(
        (models.Message.from_id == user_id) | (models.Message.to_id == user_id)
    ).offset(skip).limit(limit).all()

def mark_message_seen(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db_message.seen = True
        db.commit()
        db.refresh(db_message)
    return db_message

# Eblaghieh CRUD operations
def create_eblaghieh(db: Session, eblaghieh: schemas.EblaghiehCreate):
    db_eblaghieh = models.Eblaghieh(**eblaghieh.dict())
    db.add(db_eblaghieh)
    db.commit()
    db.refresh(db_eblaghieh)
    return db_eblaghieh

def send_to_all(db: Session, eblaghieh_data: dict):
    users = db.query(models.User).filter(models.User.active == True).all()
    eblaghieh_list = []
    for user in users:
        db_eblaghieh = models.Eblaghieh(**eblaghieh_data, to_id=user.id)
        db.add(db_eblaghieh)
        eblaghieh_list.append(db_eblaghieh)
    db.commit()
    return eblaghieh_list

# Room CRUD operations
def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def create_room_option(db: Session, room_id: int, option: str):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        if db_room.options:
            db_room.options += f",{option}"
        else:
            db_room.options = option
        db.commit()
        db.refresh(db_room)
    return db_room

def get_room_info(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

# Report CRUD operations
def create_report(db: Session, report: schemas.ReportCreate):
    db_report = models.Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def mark_report_fixed(db: Session, report_id: int):
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if db_report:
        db_report.fixed = True
        db.commit()
        db.refresh(db_report)
    return db_report

# Admin CRUD operations
def create_admin(db: Session, admin: schemas.AdminCreate):
    hashed_password = bcrypt.hashpw(admin.password.encode('utf-8'), bcrypt.gensalt())
    db_admin = models.Admin(
        name=admin.name,
        permission=admin.permission,
        password=hashed_password.decode('utf-8')
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin
    
    

# Roommate functions
def get_roommates(db: Session, user_id: int):
    """
    Get all users who share a room with the given user
    """
    # First, get all rooms the user is in
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    # Get all room IDs where the user is a member
    room_ids = [room.id for room in user.rooms]
    
    if not room_ids:
        return []
    
    # Find all other users in those rooms (excluding the current user)
    roommates = db.query(models.User).join(
        models.room_users
    ).filter(
        models.room_users.c.room_id.in_(room_ids),
        models.User.id != user_id,
        models.User.active == True,
        models.User.valid == True
    ).distinct().all()
    
    return roommates

def get_roommates_by_room(db: Session, room_id: int, exclude_user_id: Optional[int] = None):
    """
    Get all users in a specific room
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        return []
    
    query = db.query(models.User).join(
        models.room_users
    ).filter(
        models.room_users.c.room_id == room_id,
        models.User.active == True,
        models.User.valid == True
    )
    
    if exclude_user_id:
        query = query.filter(models.User.id != exclude_user_id)
    
    return query.all()

def add_user_to_room(db: Session, user_id: int, room_id: int):
    """
    Add a user to a room
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    
    if not user or not room:
        return False
    
    # Check if user is already in the room
    if room in user.rooms:
        return False
    
    user.rooms.append(room)
    db.commit()
    return True

def remove_user_from_room(db: Session, user_id: int, room_id: int):
    """
    Remove a user from a room
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    
    if not user or not room:
        return False
    
    # Check if user is in the room
    if room not in user.rooms:
        return False
    
    user.rooms.remove(room)
    db.commit()
    return True

def get_user_rooms(db: Session, user_id: int):
    """
    Get all rooms a user is in
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    return user.rooms

# Add these functions to crud.py

def update_user_payment_status(
    db: Session, 
    user_id: int, 
    has_paid: bool = True,
    amount: Optional[float] = None,
    notes: Optional[str] = None
):
    """
    Update user payment status
    """
    user = get_user(db, user_id)
    if not user:
        return None
    
    # Check if payment attributes exist
    if not hasattr(user, 'has_paid'):
        # If payment system not implemented, return None
        return None
    
    from datetime import datetime, timedelta
    
    user.has_paid = has_paid
    
    if has_paid:
        user.payment_date = datetime.utcnow()
        if amount is not None:
            user.payment_amount = int(amount * 100)  # Convert to cents
        user.next_payment_due = datetime.utcnow() + timedelta(days=30)  # Default 30 days
    else:
        user.payment_date = None
        user.payment_amount = None
    
    if notes is not None:
        user.payment_notes = notes
    
    db.commit()
    db.refresh(user)
    return user

def get_users_with_overdue_payments(db: Session):
    """
    Get users with overdue payments (placeholder implementation)
    """
    from datetime import datetime
    
    # Simple implementation - get users who haven't paid
    overdue_users = db.query(models.User).filter(
        models.User.has_paid == False,
        models.User.active == True
    ).all()
    
    # For a more advanced implementation, you would check next_payment_due date
    # current_date = datetime.utcnow()
    # overdue_users = db.query(models.User).filter(
    #     models.User.next_payment_due < current_date,
    #     models.User.active == True
    # ).all()
    
    return overdue_users

def get_payment_stats(db: Session):
    """
    Get payment statistics
    """
    total_users = db.query(models.User).filter(models.User.active == True).count()
    paid_users = db.query(models.User).filter(
        models.User.has_paid == True,
        models.User.active == True
    ).count()
    unpaid_users = total_users - paid_users
    
    total_revenue = db.query(models.User.payment_amount).filter(
        models.User.has_paid == True,
        models.User.active == True
    ).all()
    
    revenue_sum = sum([amount[0] for amount in total_revenue if amount[0] is not None]) or 0
    
    return {
        "total_users": total_users,
        "paid_users": paid_users,
        "unpaid_users": unpaid_users,
        "payment_rate": (paid_users / total_users * 100) if total_users > 0 else 0,
        "total_revenue": revenue_sum / 100,  # Convert back to currency units
        "average_payment": (revenue_sum / paid_users / 100) if paid_users > 0 else 0
    }

def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).offset(skip).limit(limit).all()

def get_reports_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Report).filter(
        models.Report.user_id == user_id
    ).offset(skip).limit(limit).all()