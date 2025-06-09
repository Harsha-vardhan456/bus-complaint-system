from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from bson.objectid import ObjectId
from functools import wraps
import jwt
import os
from email_service import send_status_update_notification

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

@admin.route('/complaints', methods=['GET'])
@admin_required
def get_all_complaints():
    try:
        from app import db
        
        # Get query parameters for filtering
        status = request.args.get('status')
        complaint_type = request.args.get('type')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if complaint_type:
            query['complaintType'] = complaint_type
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            query['date'] = {
                '$gte': start.isoformat(),
                '$lte': end.isoformat()
            }
        
        # Fetch complaints with filters
        complaints = list(db.complaints.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for complaint in complaints:
            complaint['_id'] = str(complaint['_id'])
        
        return jsonify(complaints)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin.route('/complaints/<complaint_id>/status', methods=['PUT'])
@admin_required
def update_complaint_status(complaint_id):
    try:
        from app import db
        
        data = request.get_json()
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        new_status = data['status']
        remarks = data.get('remarks', '')
        
        # Update complaint status
        result = db.complaints.update_one(
            {'_id': ObjectId(complaint_id)},
            {
                '$set': {
                    'status': new_status,
                    'remarks': remarks,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Complaint not found'}), 404
        
        # Get complaint details for email notification
        complaint = db.complaints.find_one({'_id': ObjectId(complaint_id)})
        if complaint:
            # Send email notification to user
            send_status_update_notification(
                complaint['user_email'],
                complaint_id,
                new_status,
                remarks
            )
        
        return jsonify({
            'message': 'Complaint status updated successfully',
            'status': new_status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin.route('/complaints/stats', methods=['GET'])
@admin_required
def get_complaint_stats():
    try:
        from app import db
        
        # Get total complaints count
        total_complaints = db.complaints.count_documents({})
        
        # Get complaints count by status
        status_counts = list(db.complaints.aggregate([
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
        ]))
        
        # Get complaints count by type
        type_counts = list(db.complaints.aggregate([
            {'$group': {'_id': '$complaintType', 'count': {'$sum': 1}}}
        ]))
        
        return jsonify({
            'total_complaints': total_complaints,
            'status_distribution': status_counts,
            'type_distribution': type_counts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500