
from database import Base, engine
import models

# Create tables that do not already exist
Base.metadata.create_all(bind=engine)

print("HR users table created successfully!")
