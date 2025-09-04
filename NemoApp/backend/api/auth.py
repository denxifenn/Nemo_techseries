from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Deprecated: Backend registration removed. Use Firebase Auth on frontend for signup.

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

    # Ensure user profile exists; auto-provision on first login
    user = FirebaseService.ensure_user_doc(uid)

    return jsonify({'success': True, 'user': {
        'uid': user.get('uid') or uid,
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