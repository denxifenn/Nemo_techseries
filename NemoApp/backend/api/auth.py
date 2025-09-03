from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        uid = FirebaseService.create_user(email, password, name)
        return jsonify({'success': True, 'uid': uid, 'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint expects the frontend to perform Firebase client-side authentication
    and send the ID token here for verification. The backend will verify token and
    return basic user info from Firestore.
    """
    data = request.get_json() or {}
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'success': False, 'error': 'Missing idToken'}), 400

    uid = FirebaseService.verify_token(id_token)
    if not uid:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

    user = FirebaseService.get_user(uid)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({'success': True, 'user': {
        'uid': user.get('uid'),
        'email': user.get('email'),
        'name': user.get('name'),
        'role': user.get('role', 'user')
    }}), 200

@auth_bp.route('/api/auth/verify', methods=['GET'])
def verify():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    if not token:
        return jsonify({'valid': False}), 401

    uid = FirebaseService.verify_token(token)
    if not uid:
        return jsonify({'valid': False}), 401

    return jsonify({'valid': True, 'uid': uid}), 200