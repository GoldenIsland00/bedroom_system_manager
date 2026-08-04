# endpoints.py - FIXED VERSION
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import bcrypt
import os
from datetime import datetime  # ADD THIS IMPORT

from .. import crud, schemas, models  # ADD models import
from ..database import get_db
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from ..auth import get_current_user, get_current_admin

from datetime import timedelta

router = APIRouter()




# login endpoint
@router.post("/login", response_model=schemas.Token)
def login(
    login_data: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    
    Can login with either:
    - Username
    - Student ID (std_id)
    """
    # Authenticate user
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Check if user is valid
    if not user.valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not valid"
        )
    
    # Update last login
    # user.last_login = datetime.utcnow()
    # db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "is_admin": user.is_admin
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }

# Admin login endpoint
@router.post("/admin/login", response_model=schemas.Token)
def admin_login(
    login_data: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate admin and return JWT token
    """
    # Authenticate admin
    admin = crud.authenticate_admin(db, login_data.username, login_data.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with admin flag
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": admin.name,
            "user_id": admin.id,
            "is_admin": True,
            "admin_id": admin.id
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": admin.id,
        "username": admin.name,
        "is_admin": True
    }

# Token validation endpoint
@router.get("/validate-token")
def validate_token(current_user: schemas.User = Depends(get_current_user)):
    """
    Validate the current authentication token
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "is_admin": current_user.is_admin,
            "active": current_user.active,
            "valid": current_user.valid
        }
    }

# Logout endpoint (client-side token invalidation)
@router.post("/logout")
def logout():
    """
    Logout user - client should remove token
    """
    return {"message": "Successfully logged out"}

# Password change endpoint
@router.post("/change-password")
def change_password(
    password_data: schemas.PasswordChange,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not crud.authenticate_user(db, current_user.username, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    current_user.password = hashed_password
    db.commit()
    
    return {"message": "Password changed successfully"}

# User endpoints with authentication
# @router.post("/create_users/", response_model=schemas.User)
# def create_user(
#     user: schemas.UserCreate, 
#     db: Session = Depends(get_db),
#     current_user: schemas.User = Depends(get_current_admin)  # Only admins can create users
# ):
#     db_user = crud.get_user_by_username(db, username=user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     db_user = crud.get_user_by_std_id(db, std_id=user.std_id)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Student ID already registered")
#     return crud.create_user(db=db, user=user)
# SIMPLE TEST ENDPOINT - Create test user
@router.post("/test/create-user", tags=["test"])
def create_simple_test_user(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Create a test user with just username
    """
    # Quick check - disable in production
    if os.getenv("ENV") == "production":
        return {"error": "Disabled in production"}
    
    # Auto-create user with simple password
    password = "test123"
    
    # Generate unique student ID
    import time
    std_id = f"TEST{int(time.time()) % 10000}"
    
    # Create user
    user = models.User(
        username=username,
        password=get_password_hash(password),
        std_id=std_id,
        std_of="Test Department",
        date_join=datetime.now(),
        active=True,
        valid=True,
        is_admin=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User created",
        "username": username,
        "password": password,
        "student_id": std_id,
        "user_id": user.id,
        "login_info": f"Username: {username}, Password: {password}"
    }


@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    # Users can only view their own profile unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ... rest of the endpoints remain the same

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, 
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    # Users can only update their own profile unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    return crud.update_user(db, user_id, user_update)

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin)  # Only admins can delete users
):
    crud.delete_user(db, user_id)
    return {"message": "User deleted successfully"}

# Food endpoints
@router.post("/foods/", response_model=schemas.Food)
def create_food(food: schemas.FoodCreate, db: Session = Depends(get_db)):
    return crud.create_food(db=db, food=food)

@router.get("/foods/", response_model=List[schemas.Food])
def read_foods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    foods = crud.get_foods(db, skip=skip, limit=limit)
    return foods

@router.put("/foods/{food_id}")
def update_food(food_id: int, food_data: dict, db: Session = Depends(get_db)):
    return crud.update_food(db, food_id, food_data)

@router.delete("/foods/{food_id}")
def delete_food(food_id: int, db: Session = Depends(get_db)):
    crud.delete_food(db, food_id)
    return {"message": "Food deleted successfully"}

# Message endpoints
@router.post("/messages/", response_model=schemas.Message)
def create_message(
    message: schemas.MessageCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) 
):
    """
    Create a new message (current user is the sender)
    """
    return crud.create_message(
        db=db, 
        message=message, 
        from_id=current_user.id  
    )
@router.get("/messages/{user_id}", response_model=List[schemas.Message])
def read_messages(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_messages(db, user_id, skip=skip, limit=limit)

@router.put("/messages/{message_id}/seen")
def mark_message_seen(message_id: int, db: Session = Depends(get_db)):
    return crud.mark_message_seen(db, message_id)

# Eblaghieh endpoints
@router.post("/eblaghieh/", response_model=schemas.Eblaghieh)
def create_eblaghieh(eblaghieh: schemas.EblaghiehCreate, db: Session = Depends(get_db)):
    return crud.create_eblaghieh(db=db, eblaghieh=eblaghieh)

@router.post("/eblaghieh/send-to-all/")
def send_eblaghieh_to_all(eblaghieh_data: dict, db: Session = Depends(get_db)):
    return crud.send_to_all(db, eblaghieh_data)

# Room endpoints
@router.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db=db, room=room)

@router.post("/rooms/{room_id}/options")
def add_room_option(room_id: int, option: str, db: Session = Depends(get_db)):
    return crud.create_room_option(db, room_id, option)

@router.get("/rooms/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    return crud.get_room_info(db, room_id)

# Report endpoints
@router.post("/reports/", response_model=schemas.Report)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db=db, report=report)

@router.put("/reports/{report_id}/fixed")
def mark_report_fixed(report_id: int, db: Session = Depends(get_db)):
    return crud.mark_report_fixed(db, report_id)

# Admin endpoints
@router.post("/admins/", response_model=schemas.Admin)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    return crud.create_admin(db=db, admin=admin)


# Password change endpoint
@router.post("/change-password")
def change_password(
    password_data: schemas.PasswordChange,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not crud.authenticate_user(db, current_user.username, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    current_user.password = hashed_password
    db.commit()
    
    return {"message": "Password changed successfully"}
    
# Roommates endpoint
@router.get("/users/{user_id}/roommates", response_model=schemas.RoommatesResponse)
def get_user_roommates(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    """
    Get all students who share a room with the specified user
    
    Users can only view their own roommates unless they're admin
    """
    # Users can only view their own roommates unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own roommates"
        )
    
    # Get roommates
    roommates = crud.get_roommates(db, user_id)
    
    # Get rooms shared with each roommate
    user_rooms = crud.get_user_rooms(db, user_id)
    user_room_ids = [room.id for room in user_rooms]
    
    # Prepare response
    roommate_responses = []
    for roommate in roommates:
        # Get rooms this roommate shares with the user
        shared_room_ids = []
        for room in roommate.rooms:
            if room.id in user_room_ids:
                shared_room_ids.append(room.id)
        
        roommate_responses.append(schemas.RoommateResponse(
            id=roommate.id,
            username=roommate.username,
            std_id=roommate.std_id,
            std_of=roommate.std_of,
            image=roommate.image,
            room_ids=shared_room_ids
        ))
    
    return schemas.RoommatesResponse(
        current_user_id=user_id,
        current_username=current_user.username,
        roommates=roommate_responses,
        total=len(roommate_responses),
        shared_rooms=user_room_ids
    )

@router.get("/rooms/{room_id}/roommates", response_model=List[schemas.RoommateResponse])
def get_room_roommates(
    room_id: int,
    exclude_current: bool = True,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    """
    Get all students in a specific room
    
    - exclude_current: If True, excludes the current user from the results
    """
    exclude_user_id = current_user.id if exclude_current else None
    roommates = crud.get_roommates_by_room(db, room_id, exclude_user_id)
    
    return [
        schemas.RoommateResponse(
            id=roommate.id,
            username=roommate.username,
            std_id=roommate.std_id,
            std_of=roommate.std_of,
            image=roommate.image,
            room_ids=[room_id]  # All users in this endpoint are in the same room
        )
        for roommate in roommates
    ]

@router.post("/rooms/{room_id}/users/{user_id}")
def add_user_to_room_endpoint(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin)  # Only admins can add users to rooms
):
    """
    Add a user to a room (Admin only)
    """
    success = crud.add_user_to_room(db, user_id, room_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User could not be added to room"
        )
    
    return {"message": f"User {user_id} added to room {room_id} successfully"}

@router.delete("/rooms/{room_id}/users/{user_id}")
def remove_user_from_room_endpoint(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin)  # Only admins can remove users from rooms
):
    """
    Remove a user from a room (Admin only)
    """
    success = crud.remove_user_from_room(db, user_id, room_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User could not be removed from room"
        )
    
    return {"message": f"User {user_id} removed from room {room_id} successfully"}

@router.get("/users/{user_id}/rooms", response_model=List[schemas.Room])
def get_user_rooms_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # Requires authentication
):
    """
    Get all rooms a user is in
    
    Users can only view their own rooms unless they're admin
    """
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own rooms"
        )
    
    rooms = crud.get_user_rooms(db, user_id)
    return rooms


# SIMPLE TEST ENDPOINT - Create test user
@router.post("/test/create-user", tags=["test"])
def create_simple_test_user(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Create a test user with just username - FIXED VERSION
    """
    try:
        # Quick check - disable in production
        if os.getenv("ENV") == "production":
            return {"error": "Disabled in production"}
        
        # Auto-create user with simple password
        user_password = "test123"  # Renamed to avoid conflict
        
        # Generate unique student ID
        import time
        std_id = f"TEST{int(time.time()) % 10000}"
        
        print(f"Creating user: {username}, password: {user_password}")
        
        # Hash the password
        hashed_password = get_password_hash(user_password)
        print(f"Password hashed successfully, length: {len(hashed_password)}")
        
        # Create user
        user = models.User(
            username=username,
            password=hashed_password,  # Use the hashed password
            std_id=std_id,
            std_of="Test Department",
            date_join=datetime.now(),
            active=True,
            valid=True,
            is_admin=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "User created",
            "username": username,
            "password": user_password,  # Return the plain text password for reference
            "student_id": std_id,
            "user_id": user.id,
            "login_info": f"Username: {username}, Password: {user_password}"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in create_simple_test_user: {e}")
        print(f"Traceback: {error_details}")
        
        return {
            "error": str(e),
            "details": "Check server logs for full traceback",
            "username": username
        }

# SIMPLE PAYMENT CHECK ENDPOINT
@router.get("/check-payment/{user_id}", tags=["payment"])
def simple_payment_check(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Simple payment check - no authentication for demo
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        return {"paid": False, "reason": "User not found"}
    
    # Super simple logic
    paid = user.id % 2 == 0  # Even IDs are "paid"
    
    return {
        "user_id": user_id,
        "username": user.username,
        "paid": paid,
        "reason": "Even ID = paid, Odd ID = not paid (demo)",
        "tip": "In real app, check payment database or payment gateway"
    }

# SIMPLE PAYMENT SUMMARY (Admin only)
@router.get("/payment/summary", tags=["payment"])
def payment_summary(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin)  # Admin only
):
    """
    Get simple payment summary
    """
    users = db.query(models.User).filter(models.User.active == True).all()
    
    # Simple demo logic
    paid_count = 0
    unpaid_count = 0
    
    for user in users:
        if user.id % 2 == 0:  # Even IDs are "paid"
            paid_count += 1
        else:
            unpaid_count += 1
    
    return {
        "total_users": len(users),
        "paid_users": paid_count,
        "unpaid_users": unpaid_count,
        "payment_rate": f"{(paid_count/len(users)*100):.1f}%" if users else "0%",
        "summary_date": datetime.now(),
        "note": "Demo data - even user IDs are marked as paid"
    }


@router.get("/reports/", response_model=List[schemas.Report])
def read_reports(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get all reports (for admins)
    """
    # فقط ادمین‌ها می‌توانند تمام گزارشات را ببینند
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view all reports"
        )
    
    # باید تابع get_reports را به crud.py اضافه کنیم
    reports = db.query(models.Report).offset(skip).limit(limit).all()
    return reports