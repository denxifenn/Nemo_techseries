from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Deprecated: Backend registration removed. Use Firebase Auth on frontend for signup.

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint expects the frontend to perform Firebase client-side authentication
    and send the ID token here for verification. The backend will verify token and
    return basic user info from Firestore.
    """
    logger.info("POST /api/auth/login called")
    data = request.get_json(silent=True) or {}
    body_token = (data.get('idToken') or '').strip()

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