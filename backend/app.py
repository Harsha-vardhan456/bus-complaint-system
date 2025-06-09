from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from email_validator import validate_email, EmailNotValidError
from admin_routes import admin
from password_reset import generate_reset_token, verify_reset_token, update_password
from email_templates.password_reset import send_password_reset_email

# Load environment variables
load_dotenv()

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(admin, url_prefix='/api/admin')

# MongoDB connection
try:
    client = MongoClient(os.getenv('MONGODB_URI'))
    # Test the connection
    client.admin.command('ping')
    db = client.complaint_system  # Changed to match the database name in connection string
    print('Successfully connected to MongoDB')
    # Verify collections exist or create them
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
        print('Created users collection')
    if 'complaints' not in db.list_collection_names():
        db.create_collection('complaints')
        print('Created complaints collection')
except Exception as e:
    print(f'Error connecting to MongoDB: {str(e)}')
    print('Please ensure:')
    print('1. MongoDB service is running (it is)')
    print('2. MongoDB is listening on localhost:27017')
    print('3. No authentication is required for local development')
    raise

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

# Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data', 'details': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'details': f'Please provide: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email format
        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return jsonify({
                'error': 'Invalid email format',
                'details': str(e)
            }), 400
        
        # Check if user already exists
        if db.users.find_one({'email': data['email']}):
            return jsonify({
                'error': 'Email already registered',
                'details': 'Please use a different email or try logging in'
            }), 400
        
        # Validate password
        if len(data['password']) < 8:
            return jsonify({
                'error': 'Invalid password',
                'details': 'Password must be at least 8 characters long'
            }), 400
        
        try:
            # Hash password
            hashed_password = pbkdf2_sha256.hash(data['password'])
        except Exception as e:
            logger.error(f'Password hashing error: {str(e)}')
            return jsonify({
                'error': 'Password processing error',
                'details': 'Unable to process the password. Please try again.'
            }), 500
        
        # Create user document
        user = {
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'role': 'user',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Insert user into database
            result = db.users.insert_one(user)
            if not result.inserted_id:
                raise Exception('Failed to insert user into database')
        except Exception as e:
            logger.error(f'Database error during registration: {str(e)}')
            return jsonify({
                'error': 'Database error',
                'details': 'Failed to create user account. Please try again later.'
            }), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'details': 'You can now log in with your email and password'
        }), 201
    
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return jsonify({
            'error': 'Server error',
            'details': 'An unexpected error occurred during registration. Please try again later.'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request data',
                'details': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        missing_fields = [field for field in ['email', 'password'] if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'details': f'Please provide: {", ".join(missing_fields)}'
            }), 400
        
        # Find user
        user = db.users.find_one({'email': data['email']})
        if not user:
            return jsonify({
                'error': 'Authentication failed',
                'details': 'No account found with this email. Please check your email or register for a new account.'
            }), 401
        
        # Verify password
        try:
            if not pbkdf2_sha256.verify(data['password'], user['password']):
                return jsonify({
                    'error': 'Authentication failed',
                    'details': 'Incorrect password. Please try again or use the password reset option.'
                }), 401
        except Exception as e:
            logger.error(f'Password verification error: {str(e)}')
            return jsonify({
                'error': 'Authentication failed',
                'details': 'Invalid password format. Please try registering again.'
            }), 401
        
        try:
            # Generate JWT token
            token = jwt.encode({
                'user_id': str(user['_id']),
                'email': user['email'],
                'role': user['role'],
                'exp': datetime.now().astimezone().replace(microsecond=0) + timedelta(days=1)
            }, JWT_SECRET_KEY)
        except Exception as e:
            logger.error(f'Token generation error: {str(e)}')
            return jsonify({
                'error': 'Authentication failed',
                'details': 'Failed to generate authentication token. Please try again.'
            }), 500
        
        return jsonify({
            'token': token,
            'user': {
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            },
            'message': 'Login successful'
        })
    
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return jsonify({
            'error': 'Server error',
            'details': 'An unexpected error occurred during login. Our team has been notified. Please try again later.'
        }), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        user = db.users.find_one({'email': data['email']})
        if not user:
            # Return success even if email not found for security
            return jsonify({'message': 'If your email is registered, you will receive password reset instructions'}), 200

        # Generate reset token
        reset_token = generate_reset_token(data['email'])

        # Send password reset email
        if not send_password_reset_email(data['email'], reset_token):
            return jsonify({'error': 'Failed to send password reset email'}), 500

        return jsonify({'message': 'Password reset instructions sent to your email'}), 200

    except Exception as e:
        logger.error(f'Forgot password error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        if not all(key in data for key in ['token', 'new_password']):
            return jsonify({'error': 'Token and new password are required'}), 400

        # Verify reset token
        email = verify_reset_token(data['token'])
        if not email:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Update password
        if not update_password(db, email, data['new_password']):
            return jsonify({'error': 'Failed to update password'}), 500

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        logger.error(f'Reset password error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/complaints', methods=['POST'])
def submit_complaint():
    try:
        # Get user from JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        data = request.get_json()
        
        # Validate required fields
        required_fields = ['busNumber', 'routeNumber', 'complaintType', 'description', 'location', 'date']
        if not all(key in data for key in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check for duplicate complaints
        start_of_day = datetime.strptime(data['date'], '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        existing_complaint = db.complaints.find_one({
            'busNumber': data['busNumber'],
            'routeNumber': data['routeNumber'],
            'complaintType': data['complaintType'],
            'created_at': {'$gte': start_of_day, '$lt': end_of_day}
        })
        
        if existing_complaint:
            return jsonify({
                'error': 'Duplicate complaint',
                'details': 'A similar complaint has already been submitted today for this bus and route',
                'existing_complaint_id': str(existing_complaint['_id'])
            }), 409
        
        # Create complaint document
        complaint = {
            **data,
            'user_email': user_email,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert complaint into database
        result = db.complaints.insert_one(complaint)
        tracking_id = str(result.inserted_id)

        # Send confirmation email
        from email_service import send_complaint_confirmation
        if not send_complaint_confirmation(user_email, tracking_id, data):
            # Log the error but don't fail the complaint submission
            app.logger.error(f'Failed to send confirmation email to {user_email}')
            return jsonify({
                'message': 'Complaint submitted successfully but email notification failed',
                'tracking_id': tracking_id
            }), 201
        
        return jsonify({
            'message': 'Complaint submitted successfully',
            'tracking_id': tracking_id
        }), 201
    
    except Exception as e:
        app.logger.error(f'Error in submit_complaint: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/complaints/<tracking_id>', methods=['GET'])
def track_complaint(tracking_id):
    try:
        from bson.objectid import ObjectId
        
        # Find complaint
        complaint = db.complaints.find_one({'_id': ObjectId(tracking_id)})
        if not complaint:
            return jsonify({'error': 'Complaint not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        complaint['_id'] = str(complaint['_id'])
        
        return jsonify(complaint)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complaints/user', methods=['GET'])
def get_user_complaints():
    try:
        # Get user from JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Fetch user's complaints
        complaints = list(db.complaints.find({'user_email': user_email}).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for complaint in complaints:
            complaint['_id'] = str(complaint['_id'])
        
        return jsonify(complaints)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Root route
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Welcome to the Bus Complaint System API',
        'version': '1.0',
        'status': 'running'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)