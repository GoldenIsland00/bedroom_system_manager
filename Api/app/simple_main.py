from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import bcrypt

# Database setup
DATABASE_URL = "sqlite:///./Bed.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    std_id = Column(String, unique=True, index=True)
    password = Column(String)
    date_join = Column(DateTime, default=datetime.utcnow)
    std_of = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    valid = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Bed System", version="1.0.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bed System API", "version": "1.0.0"}

@app.post("/users/")
def create_user(username: str, std_id: str, password: str, std_of: Optional[str] = None, db: Session = Depends(get_db)):
    # Check if user exists
    user_exists = db.query(User).filter(
        (User.username == username) | (User.std_id == std_id)
    ).first()
    
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    db_user = User(
        username=username,
        std_id=std_id,
        password=hashed_password.decode('utf-8'),
        std_of=std_of,
        date_join=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "std_id": db_user.std_id,
        "message": "User created successfully"
    }

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "std_id": user.std_id,
            "active": user.active,
            "date_join": user.date_join
        }
        for user in users
    ]

@app.get("/Bed")
def show_Bed():
    """Simple Bed visualization endpoint"""
    return {
        "entities": [
            {"name": "Users", "attributes": ["id", "username", "std_id", "password", "date_join"]},
            {"name": "Food", "attributes": ["id", "food_name", "date", "price", "reserved"]},
            {"name": "Message", "attributes": ["id", "from_id", "to_id", "date", "content"]},
        ],
        "relationships": [
            {"from": "Users", "to": "Food", "type": "has_many"},
            {"from": "Users", "to": "Message", "type": "sends/receives"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)