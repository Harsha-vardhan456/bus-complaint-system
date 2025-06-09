from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_admin():
    try:
        # Connect to MongoDB
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.complaint_system

        # Check if admin user exists
        admin_user = db.users.find_one({'email': 'admin@example.com'})
        
        if not admin_user:
            # Create admin user
            admin = {
                'name': 'Admin',
                'email': 'admin@example.com',
                'password': pbkdf2_sha256.hash('admin123'),
                'role': 'admin',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Insert admin into database
            db.users.insert_one(admin)
            print('Admin user created successfully')
        else:
            print('Admin user already exists')

    except Exception as e:
        print(f'Error initializing admin user: {str(e)}')

if __name__ == '__main__':
    init_admin()