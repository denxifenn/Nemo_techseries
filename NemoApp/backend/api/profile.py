from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db, FirebaseService
from firebase_admin import firestore as admin_fs

# Profile Blueprint (MVP)
# Provides Firestore-backed profile view/update for the current user.

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get current user's profile.
    Auto-provision a minimal user document if it doesn't exist yet.
    """
    try:
        user = FirebaseService.ensure_user_doc(current_user)
        profile = {
            'uid': user.get('uid', current_user),
            'email': user.get('email'),
            'phoneNumber': user.get('phoneNumber'),
            'name': user.get('name'),
            'role': user.get('role', 'user'),
            'profilePicture': user.get('profilePicture', ''),
            'friends': user.get('friends', []),
            'createdAt': user.get('createdAt')
        }
        return jsonify({'success': True, 'profile': profile}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@profile_bp.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """
    Update current user's profile.
    Accepts any of:
      - name: string (1..100)
      - profilePicture: string (URL or path)
    """
    try:
        body = request.get_json(silent=True) or {}

        updates = {}
        # Validate and collect fields
        if 'name' in body and isinstance(body['name'], str):
            name = body['name'].strip()
            if 1 <= len(name) <= 100:
                updates['name'] = name
            else:
                return jsonify({'success': False, 'error': 'Invalid name length'}), 400

        if 'profilePicture' in body and isinstance(body['profilePicture'], str):
            updates['profilePicture'] = body['profilePicture'].strip()

        if not updates:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400

        # Use server timestamp in storage, but do not return the sentinel in JSON
        updates['updatedAt'] = admin_fs.SERVER_TIMESTAMP

        doc_ref = db.collection('users').document(current_user)
        doc_ref.set(updates, merge=True)

        # Build a safe JSON response (exclude non-serializable sentinel value)
        response_updates = {k: v for k, v in updates.items() if k != 'updatedAt'}

        return jsonify({'success': True, 'message': 'Profile updated', 'updated': response_updates}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500