# main.py - FIXED VERSION
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .api.endpoints import router as api_router
from .api.visualization import router as edr_router
from .database import SessionLocal
# Remove this: from . import crud, schemas  # Not needed here
from .auth import get_password_hash  # CORRECT - relative import
import bcrypt

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bed System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(edr_router, tags=["edr"])

@app.get("/")
async def root():
    return {"message": "Bed System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}



@app.on_event("startup")
def startup_event():
    """Create default admin user on startup"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(models.Admin).filter(models.Admin.name == "admin").first()
        if not admin:
            # Create default admin - استفاده از bcrypt مستقیم
            try:
                # استفاده از bcrypt با مدیریت محدودیت
                password = "admin123"
                # اطمینان از محدودیت 72 بایتی
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password = password_bytes[:72].decode('utf-8', 'ignore')
                
                hashed_password = bcrypt.hashpw(
                    password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                admin = models.Admin(
                    name="admin",
                    permission="superadmin",
                    password=hashed_password
                )
                db.add(admin)
                db.commit()
                print("✅ Default admin created: admin / admin123")
            except Exception as e:
                print(f"❌ Error creating admin: {e}")
                # استفاده از رمز عبور ساده در صورت شکست
                admin = models.Admin(
                    name="admin",
                    permission="superadmin",
                    password="admin123"  # plain text - فقط برای توسعه
                )
                db.add(admin)
                db.commit()
                print("⚠️ Default admin created with plain text password (development only)")
        
        # Check if any regular admin user exists
        user_admin = db.query(models.User).filter(models.User.is_admin == True).first()
        if not user_admin:
            try:
                # Create a default user admin
                password = "admin123"
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password = password_bytes[:72].decode('utf-8', 'ignore')
                
                hashed_password = bcrypt.hashpw(
                    password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                admin_user = models.User(
                    username="admin_user",
                    std_id="admin001",
                    password=hashed_password,
                    std_of="Administration",
                    is_admin=True,
                    active=True,
                    valid=True
                )
                db.add(admin_user)
                db.commit()
                print("✅ Default user admin created: admin_user / admin123")
            except Exception as e:
                print(f"❌ Error creating user admin: {e}")
                # Fallback to simple method
                from .auth import get_password_hash
                admin_user = models.User(
                    username="admin_user",
                    std_id="admin001",
                    password=get_password_hash("admin123"),
                    std_of="Administration",
                    is_admin=True,
                    active=True,
                    valid=True
                )
                db.add(admin_user)
                db.commit()
                print("✅ Default user admin created with fallback method")
    except Exception as e:
        print(f"⚠️ Startup event error: {e}")
        db.rollback()
    finally:
        db.close()

# If you want to run without uvicorn command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)