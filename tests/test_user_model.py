import sys
import os
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import init_db, get_session, engine
from app.db.models import User
from sqlmodel import Session, select

def test_create_user():
    print("Initializing database...")
    init_db()
    
    print("Creating user...")
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_secret",
        phone="1234567890"
    )
    
    with Session(engine) as session:
        # Check if user already exists to avoid unique constraint error
        statement = select(User).where(User.email == "test@example.com")
        existing_user = session.exec(statement).first()
        if existing_user:
            print("User already exists, deleting...")
            session.delete(existing_user)
            session.commit()
            
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"User created: {user}")
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        print("Verification successful!")

if __name__ == "__main__":
    test_create_user()
