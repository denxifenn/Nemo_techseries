from flask import Blueprint, jsonify, request
from utils.decorators import require_admin
from services.firebase_service import db
from firebase_admin import firestore as admin_fs
from datetime import datetime

# Admin Blueprint (MVP) - Firestore-backed event creation

admin_bp = Blueprint('admin', __name__)

def _combine_date_time(date_str: str, time_str: str):
    """
    Combine 'YYYY-MM-DD' and 'HH:MM' into a naive datetime for comparison.
    Returns None if parsing fails.
    """
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except Exception:
        return None

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
    allowed_categories = {"sports", "workshop", "social", "cultural"}
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

    # Disallow creating events scheduled in the past (relative to current UTC time)
    event_dt = _combine_date_time(date, time)
    if not event_dt:
        return jsonify({"success": False, "error": "Invalid date/time combination"}), 400
    if event_dt <= datetime.utcnow():
        return jsonify({"success": False, "error": "Event start must be in the future"}), 400

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


@admin_bp.route('/api/admin/events/<event_id>', methods=['PUT'])
@require_admin
def update_event(current_user, event_id: str):
    """
    Update an existing event (admin only).
    Accepts any subset of:
      - title, description, category, location, date, time, maxParticipants, imageUrl
    Validation:
      - category (if provided) must be in allowed set
      - date/time (if provided) must not result in a past scheduled time
      - maxParticipants (if provided) must be >= currentParticipants
    """
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict) or not body:
        return jsonify({"success": False, "error": "No fields provided"}), 400

    # Load current event
    ref = db.collection("events").document(event_id)
    snap = ref.get()
    if not snap.exists:
        return jsonify({"success": False, "error": "Event not found"}), 404
    current = snap.to_dict() or {}

    updates = {}
    allowed_categories = {"sports", "workshop", "social", "cultural"}

    # Title/Description/Location/Image
    for k in ("title", "description", "location", "imageUrl"):
        if k in body and isinstance(body[k], str):
            updates[k] = body[k].strip()

    # Category
    if "category" in body:
        cat = str(body.get("category") or "").strip().lower()
        if cat and cat not in allowed_categories:
            return jsonify({"success": False, "error": f"Invalid category. Allowed: {', '.join(sorted(allowed_categories))}"}), 400
        updates["category"] = cat

    # Date/Time
    new_date = current.get("date")
    new_time = current.get("time")
    if "date" in body:
        d = str(body.get("date") or "").strip()
        if d and len(d.split("-")) != 3:
            return jsonify({"success": False, "error": "Invalid date format; expected YYYY-MM-DD"}), 400
        new_date = d or new_date
        updates["date"] = new_date
    if "time" in body:
        t = str(body.get("time") or "").strip()
        if t and len(t.split(":")) != 2:
            return jsonify({"success": False, "error": "Invalid time format; expected HH:MM (24h)"}), 400
        new_time = t or new_time
        updates["time"] = new_time

    # If date/time changed (or provided), ensure not in the past
    if ("date" in body) or ("time" in body):
        event_dt = _combine_date_time(new_date, new_time)
        if not event_dt:
            return jsonify({"success": False, "error": "Invalid date/time combination"}), 400
        if event_dt <= datetime.utcnow():
            return jsonify({"success": False, "error": "Event start must be in the future"}), 400

    # maxParticipants check (must be >= currentParticipants)
    if "maxParticipants" in body:
        try:
            new_max = int(body.get("maxParticipants"))
            if new_max <= 0:
                raise ValueError
        except Exception:
            return jsonify({"success": False, "error": "maxParticipants must be a positive integer"}), 400
        current_part = int(current.get("currentParticipants", 0) or 0)
        if new_max < current_part:
            return jsonify({"success": False, "error": f"maxParticipants cannot be less than currentParticipants ({current_part})"}), 400
        updates["maxParticipants"] = new_max

    if not updates:
        return jsonify({"success": False, "error": "No valid fields to update"}), 400

    try:
        ref.set(updates, merge=True)
        return jsonify({"success": True, "message": "Event updated", "updated": updates}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500