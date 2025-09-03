from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db
from firebase_admin import firestore as admin_fs

# Profile Blueprint (MVP)
# Provides Firestore-backed profile view/update for the current user.

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get current user's profile.
    Returns a subset of the user document to avoid leaking internal fields.
    """
    try:
        snap = db.collection('users').document(current_user).get()
        if not snap.exists:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        data = snap.to_dict() or {}
        profile = {
            'uid': data.get('uid', current_user),
            'email': data.get('email'),
            'name': data.get('name'),
            'role': data.get('role', 'user'),
            'profilePicture': data.get('profilePicture', ''),
            'friends': data.get('friends', []),
            'createdAt': data.get('createdAt')
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

        updates['updatedAt'] = admin_fs.SERVER_TIMESTAMP

        db.collection('users').document(current_user).set(updates, merge=True)

        return jsonify({'success': True, 'message': 'Profile updated', 'updated': updates}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500