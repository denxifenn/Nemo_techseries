from flask import Blueprint, jsonify, request
from utils.decorators import require_auth

# Skeleton Bookings Blueprint (MVP stub)
# Protected with auth decorators; Firestore logic will be added next.

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/api/bookings/individual', methods=['POST'])
@require_auth
def create_individual_booking(current_user):
    """
    Create an individual booking (stub).
    Body (future): {"eventId": "..."}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "payload": body,
        "message": "Individual booking stub - to be implemented"
    }), 201

@bookings_bp.route('/api/bookings/group', methods=['POST'])
@require_auth
def create_group_booking(current_user):
    """
    Create a group booking (stub).
    Body (future): {"eventId": "...", "groupMembers": ["uid1","uid2"]}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "payload": body,
        "message": "Group booking stub - to be implemented"
    }), 201

@bookings_bp.route('/api/bookings/my', methods=['GET'])
@require_auth
def list_my_bookings(current_user):
    """
    Get current user's bookings (stub).
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "bookings": [],
        "message": "My bookings stub - to be implemented"
    }), 200