from flask import Blueprint, jsonify, request
from utils.decorators import require_auth

# Skeleton Profile Blueprint (MVP stub)
# Now protected with auth decorators; Firestore logic will be added next.

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get current user's profile (stub).
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "profile": {},
        "message": "Profile GET stub - to be implemented"
    }), 200

@profile_bp.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """
    Update current user's profile (stub).
    Body (future): {"name": "...", "profilePicture": "..."}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "payload": body,
        "message": "Profile UPDATE stub - to be implemented"
    }), 200