from datetime import datetime, timedelta
import jwt
import os
from email_service import send_password_reset_email
from passlib.hash import pbkdf2_sha256

def generate_reset_token(email):
    """Generate a password reset token."""
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({
        'email': email,
        'exp': expiration,
        'purpose': 'password_reset'
    }, os.getenv('JWT_SECRET_KEY'))
    return token

def verify_reset_token(token):
    """Verify the password reset token."""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        if payload.get('purpose') != 'password_reset':
            return None
        return payload['email']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def update_password(db, email, new_password):
    """Update user's password in the database."""
    try:
        hashed_password = pbkdf2_sha256.hash(new_password)
        result = db.users.update_one(
            {'email': email},
            {'$set': {'password': hashed_password}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f'Error updating password: {str(e)}')
        return False