from flask import Blueprint, jsonify, request
from utils.decorators import require_admin
from services.firebase_service import db
from firebase_admin import firestore as admin_fs

# Admin Blueprint (MVP) - Firestore-backed event creation

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/health', methods=['GET'])
@require_admin
def admin_health(current_user):
    """
    Health check for admin routes.
    """
    return jsonify({
        "success": True,
        "user": current_user,
        "message": "Admin routes available"
    }), 200


@admin_bp.route('/api/admin/events', methods=['POST'])
@require_admin
def create_event(current_user):
    """
    Create a new event.

    Body:
    {
      "title": "string (required)",
      "description": "string (required)",
      "category": "sports|workshop|social",  // required
      "location": "string (required)",
      "date": "YYYY-MM-DD",                  // required
      "time": "HH:MM",                        // required (24h)
      "maxParticipants": 20,                  // required (int > 0)
      "imageUrl": "optional"
    }
    """
    body = request.get_json(silent=True) or {}

    # Required fields and minimal validation
    required_fields = ["title", "description", "category", "location", "date", "time", "maxParticipants"]
    missing = [f for f in required_fields if body.get(f) in (None, "", [])]
    if missing:
        return jsonify({"success": False, "error": f"Missing field(s): {', '.join(missing)}"}), 400

    title = str(body.get("title")).strip()
    description = str(body.get("description")).strip()
    category = str(body.get("category")).strip().lower()
    location = str(body.get("location")).strip()
    date = str(body.get("date")).strip()
    time = str(body.get("time")).strip()
    imageUrl = str(body.get("imageUrl")).strip() if body.get("imageUrl") else ""

    # Category whitelist (MVP)
    allowed_categories = {"sports", "workshop", "social"}
    if category not in allowed_categories:
        return jsonify({"success": False, "error": f"Invalid category. Allowed: {', '.join(sorted(allowed_categories))}"}), 400

    # maxParticipants must be positive integer
    try:
        max_part = int(body.get("maxParticipants"))
        if max_part <= 0:
            raise ValueError
    except Exception:
        return jsonify({"success": False, "error": "maxParticipants must be a positive integer"}), 400

    # Basic format checks (lightweight)
    if len(date.split("-")) != 3:
        return jsonify({"success": False, "error": "Invalid date format; expected YYYY-MM-DD"}), 400
    if len(time.split(":")) != 2:
        return jsonify({"success": False, "error": "Invalid time format; expected HH:MM (24h)"}), 400

    # Compose event doc
    event = {
        "title": title,
        "description": description,
        "category": category,
        "imageUrl": imageUrl,
        "location": location,
        "date": date,
        "time": time,
        "maxParticipants": max_part,
        "currentParticipants": 0,
        "participants": [],
        "guestEntries": [],          # for guest name bookings
        "createdBy": current_user,
        "status": "upcoming",
        "createdAt": admin_fs.SERVER_TIMESTAMP
    }

    try:
        ref = db.collection("events").add(event)[1]
        return jsonify({
            "success": True,
            "eventId": ref.id,
            "message": "Event created successfully"
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500