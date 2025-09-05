from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, db
from datetime import datetime
from utils.phone_utils import format_singapore_phone

auth_bp = Blueprint('auth', __name__)

# Deprecated: Backend registration removed. Use Firebase Auth on frontend for signup.

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Backend login handshake.
    - Frontend signs in with Firebase client SDK (email+password via phone alias).
    - Frontend sends the Firebase ID token here.
    - Optionally accepts phoneNumber and name to enrich the user doc on first login.
    """
    data = request.get_json() or {}
    id_token = data.get('idToken')
    phone_number = data.get('phoneNumber')  # optional, free-form from client
    name = data.get('name')  # optional display name

    if not id_token:
        return jsonify({'success': False, 'error': 'Missing idToken'}), 400

    uid = FirebaseService.verify_token(id_token)
    if not uid:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

    # Normalize Singapore phone to E.164 (+65XXXXXXXX) if provided; ignore invalid formats
    normalized_phone = None
    if phone_number:
        try:
            normalized_phone = format_singapore_phone(phone_number)
        except Exception:
            normalized_phone = None

    # Ensure user profile exists; auto-provision on first login, merge phoneNumber/name if provided
    user = FirebaseService.ensure_user_doc(uid, email=None, name=name, phoneNumber=normalized_phone)

    return jsonify({'success': True, 'user': {
        'uid': user.get('uid') or uid,
        'phoneNumber': user.get('phoneNumber'),
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