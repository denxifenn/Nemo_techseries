from flask import Blueprint, jsonify, request
from utils.decorators import require_admin

# Skeleton Admin Blueprint (MVP stub)
# Protected with @require_admin; Firestore create-event logic will be added next.

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/health', methods=['GET'])
@require_admin
def admin_health(current_user):
    """
    Health check for admin routes (stub).
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "message": "Admin routes available (stub)"
    }), 200

@admin_bp.route('/api/admin/events', methods=['POST'])
@require_admin
def create_event(current_user):
    """
    Create a new event (stub).
    Body (future):
    {
      "title": "...",
      "description": "...",
      "category": "sports|workshop|social",
      "location": "...",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "maxParticipants": 20,
      "imageUrl": "optional"
    }
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "event": body,
        "message": "Create event stub - to be implemented with Firestore and admin auth"
    }), 201