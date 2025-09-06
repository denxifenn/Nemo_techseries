from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, db
from datetime import datetime
import logging
from utils.phone_utils import format_singapore_phone


logger = logging.getLogger(__name__)
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
    logger.info("POST /api/auth/login called")
    # data = request.get_json() or {}
    # id_token = data.get('idToken')
    data = request.get_json(silent=True) or {}
    body_token = (data.get('idToken') or '').strip()
    # phone_number = data.get('phoneNumber')  # optional, free-form from client
    # name = data.get('name')  # optional display name
    # fin_number = data.get('finNumber')  # optional, but recommended to be provided at signup

    # Also support Authorization: Bearer <token> as a fallback
    auth_header = request.headers.get('Authorization', '')
    header_token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''

    tokens_to_try = [t for t in [body_token, header_token] if t]

    if not tokens_to_try:
        logger.warning("No token provided (neither idToken in body nor Authorization header)")
        return jsonify({'success': False, 'error': 'Missing idToken'}), 400

    uid = None
    for idx, tkn in enumerate(tokens_to_try, start=1):
        try_len = len(tkn)
        logger.info(f"Verifying token candidate #{idx} (length={try_len})")
        uid = FirebaseService.verify_token(tkn)
        if uid:
            break

    if not uid:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401
    
    # Ensure user profile exists; auto-provision on first login
    user = FirebaseService.ensure_user_doc(uid)

    # # Normalize Singapore phone to E.164 (+65XXXXXXXX) if provided; ignore invalid formats
    # normalized_phone = None
    # if phone_number:
    #     try:
    #         normalized_phone = format_singapore_phone(phone_number)
    #     except Exception:
    #         normalized_phone = None

    # # Check FIN uniqueness if provided
    # if fin_number:
    #     fin_upper = str(fin_number).strip().upper()
    #     # Check if FIN already exists for a different user
    #     existing_users = db.collection('users').where('finNumber', '==', fin_upper).limit(1).get()
    #     for doc in existing_users:
    #         if doc.id != uid:  # FIN belongs to a different user
    #             return jsonify({'success': False, 'error': 'FIN number already registered to another account'}), 400

    # # Ensure user profile exists; auto-provision on first login, merge phoneNumber/name/finNumber if provided
    # user = FirebaseService.ensure_user_doc(uid, email=None, name=name, phoneNumber=normalized_phone, finNumber=fin_number)

    return jsonify({'success': True, 'user': {
        'uid': user.get('uid') or uid,
        'phoneNumber': user.get('phoneNumber'),
        'fullName': user.get('fullName', user.get('name')),
        'name': user.get('fullName', user.get('name')),  # legacy alias
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