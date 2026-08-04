from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class TestUserCreate(BaseModel):
    username: str
    password: str = "test123"
    std_id: str
    is_admin: bool = False
    create_admin: bool = False  # Whether to also create an admin user

class PaymentStatus(BaseModel):
    user_id: int
    has_paid: bool
    payment_date: Optional[datetime] = None
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None

# login schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    is_admin: bool = False

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

# User Schemas
class UserBase(BaseModel):
    username: str
    std_id: str
    std_of: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    std_id: Optional[str] = None
    std_of: Optional[str] = None
    active: Optional[bool] = None
    valid: Optional[bool] = None
    image: Optional[str] = None

class User(UserBase):
    id: int
    date_join: datetime
    active: bool
    valid: bool
    image: Optional[str] = None
    
    class Config:
        from_attributes = True

# Food Schemas
class FoodBase(BaseModel):
    food_name: str
    price: Optional[int] = None
    reserved: bool = False
    active: bool = True
    contain: Optional[str] = None

class FoodCreate(FoodBase):
    user_id: int

class Food(FoodBase):
    id: int
    date: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    to_id: int

class Message(MessageBase):
    id: int
    from_id: int
    to_id: int
    date: datetime
    seen: bool
    
    class Config:
        from_attributes = True

# Eblaghieh Schemas
class EblaghiehBase(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    is_res: bool = False

class EblaghiehCreate(EblaghiehBase):
    to_id: int

class Eblaghieh(EblaghiehBase):
    id: int
    to_id: int
    date: datetime
    
    class Config:
        from_attributes = True

# Room Schemas
class RoomBase(BaseModel):
    bed_num: int
    options: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    
    class Config:
        from_attributes = True

# Report Schemas
class ReportBase(BaseModel):
    cont: str
    room_id: int

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    date: datetime
    seen: bool
    fixed: bool
    
    class Config:
        from_attributes = True

# Admin Schemas
class AdminBase(BaseModel):
    name: str
    permission: str

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int
    img: Optional[str] = None
    
    class Config:
        from_attributes = True
        
        
class RoommateResponse(BaseModel):
    id: int
    username: str
    std_id: str
    std_of: Optional[str] = None
    image: Optional[str] = None
    room_ids: List[int]  # IDs of shared rooms
    
    class Config:
        from_attributes = True

class RoommatesResponse(BaseModel):
    current_user_id: int
    current_username: str
    roommates: List[RoommateResponse]
    total: int
    shared_rooms: List[int] 
