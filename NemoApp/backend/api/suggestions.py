from flask import Blueprint, jsonify, request
from utils.decorators import require_auth, require_admin

# Skeleton Suggestions Blueprint (MVP stub)
# Now protected with auth/admin decorators; Firestore logic will be added next.

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/api/suggestions', methods=['POST'])
@require_auth
def create_suggestion(current_user):
    """
    Submit an event suggestion (stub).
    Body (future): {"title": "...", "description": "...", "category": "workshop|sports|social"}
    """
    body = request.get_json(silent=True) or {}
    return jsonify({
        "success": True,
        "user": current_user,
        "suggestion": body,
        "message": "Suggestion create stub - to be implemented"
    }), 201

@suggestions_bp.route('/api/suggestions', methods=['GET'])
@require_admin
def list_suggestions(current_user):
    """
    List all suggestions (admin only in MVP) (stub).
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "suggestions": [],
        "message": "Suggestions list stub - to be implemented"
    }), 200