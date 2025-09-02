from functools import wraps
from flask import request, jsonify
from services.firebase_service import FirebaseService, db

def _get_bearer_token() -> str | None:
    """Extract 'Bearer <token>' from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.replace('Bearer ', '', 1).strip() or None

def require_auth(func):
    """
    Decorator to require a valid Firebase ID token.
    Injects current_user (uid) as the first argument to the wrapped function.
    Usage:
        @require_auth
        def my_route(current_user): ...
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        token = _get_bearer_token()
        if not token:
            return jsonify({'success': False, 'error': 'Missing or invalid Authorization header'}), 401

        uid = FirebaseService.verify_token(token)
        if not uid:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401

        return func(uid, *args, **kwargs)
    return _wrapper

def require_admin(func):
    """
    Decorator to require a valid Firebase ID token AND admin role.
    Injects current_user (uid) as the first argument to the wrapped function.
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        token = _get_bearer_token()
        if not token:
            return jsonify({'success': False, 'error': 'Missing or invalid Authorization header'}), 401

        uid = FirebaseService.verify_token(token)
        if not uid:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401

        # Check admin role in Firestore users collection
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists or user_doc.to_dict().get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403

        return func(uid, *args, **kwargs)
    return _wrapper