import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
import app.models  # Loads all models

def init_db():
    print("Connecting to PostgreSQL and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    init_db()