from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for Room-User many-to-many relationship
room_users = Table(
    'room_users',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('rooms.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords
    std_id = Column(String(50), unique=True, index=True)
    date_join = Column(DateTime, default=func.now())
    std_of = Column(String(100))
    active = Column(Boolean, default=True)
    valid = Column(Boolean, default=True)
    image = Column(Text, nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships - FIXED
    foods = relationship("Food", back_populates="user")
    messages_sent = relationship("Message", foreign_keys="Message.from_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.to_id", back_populates="receiver")
    reports = relationship("Report", back_populates="user")
    rooms = relationship("Room", secondary=room_users, back_populates="users")  # ADD THIS
    eblaghieh = relationship("Eblaghieh", foreign_keys="Eblaghieh.to_id", back_populates="receiver")  # ADD THIS

    # Add these payment-related columns
    has_paid = Column(Boolean, default=False)
    payment_date = Column(DateTime, nullable=True)
    payment_amount = Column(Integer, nullable=True)  # Store in smallest currency unit (e.g., cents)
    next_payment_due = Column(DateTime, nullable=True)
    payment_notes = Column(Text, nullable=True)

class Food(Base):
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String(100), nullable=False)
    date = Column(DateTime, default=func.now())
    price = Column(Integer)
    reserved = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    contain = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="foods")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=func.now())
    seen = Column(Boolean, default=False)
    content = Column(Text, nullable=False)
    
    sender = relationship("User", foreign_keys=[from_id], back_populates="messages_sent")  # FIXED
    receiver = relationship("User", foreign_keys=[to_id], back_populates="messages_received")  # FIXED

class Eblaghieh(Base):
    __tablename__ = "eblaghieh"
    
    id = Column(Integer, primary_key=True, index=True)
    to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_res = Column(Boolean, default=False)
    date = Column(DateTime, default=func.now())
    topic = Column(String(200))
    content = Column(Text)
    
    receiver = relationship("User", foreign_keys=[to_id], back_populates="eblaghieh")  # FIXED

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    bed_num = Column(Integer, nullable=False)
    options = Column(String(255))
    
    users = relationship("User", secondary=room_users, back_populates="rooms")  # FIXED
    reports = relationship("Report", back_populates="room")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    cont = Column(Text, nullable=False)
    date = Column(DateTime, default=func.now())
    seen = Column(Boolean, default=False)
    fixed = Column(Boolean, default=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ADD THIS to track who made the report
    
    room = relationship("Room", back_populates="reports")
    user = relationship("User", back_populates="reports")  # ADD THIS

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    permission = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    img = Column(String(255))
