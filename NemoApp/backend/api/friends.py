from flask import Blueprint, jsonify, request
from utils.decorators import require_auth

# Skeleton Friends Blueprint (MVP stub)
# Protected with auth decorators; Firestore logic will be added next.

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/api/friends/request', methods=['POST'])
@require_auth
def send_friend_request(current_user):
    """
    Send a friend request (stub).
    Body (future): {"email": "friend@example.com"}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "request": {"to": body.get("email")},
        "message": "Friend request stub - to be implemented"
    }), 201

@friends_bp.route('/api/friends/request/<request_id>', methods=['PUT'])
@require_auth
def handle_friend_request(current_user, request_id: str):
    """
    Accept or reject friend request (stub).
    Body (future): {"action": "accept" | "reject"}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "requestId": request_id,
        "action": body.get("action"),
        "message": "Friend request handle stub - to be implemented"
    }), 200

@friends_bp.route('/api/friends', methods=['GET'])
@require_auth
def list_friends(current_user):
    """
    Get current user's friends (stub).
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "friends": [],
        "message": "Friends list stub - to be implemented"
    }), 200