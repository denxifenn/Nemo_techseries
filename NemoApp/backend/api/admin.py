from flask import Blueprint, jsonify, request
from utils.decorators import require_admin
from services.firebase_service import db
from firebase_admin import firestore as admin_fs
from datetime import datetime
from utils.validators import (
    validate_event_format,
    validate_event_venue_type,
    validate_event_type,
    validate_event_region,
    validate_date,
    validate_hhmm_time,
    derive_timing_bucket,
    validate_price_float,
    ensure_start_before_end,
    add_minutes_to_hhmm,
)

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
    Create a new event with extended schema.

    Accepts new schema (recommended) and maps legacy fields for compatibility.

    New schema body:
    {
      "title": "string (required)",
      "description": "string (required)",
      "format": "online" | "offline",
      "venueType": "indoor" | "outdoor",    // required if format == "offline"
      "type": "sports" | "arts" | "culture" | "music" | "performance" | "workshop" | "tours" | "other",
      "region": "north" | "south" | "east" | "west" | "central",
      "organiser": "free-text",
      "location": "string (required)",
      "date": "YYYY-MM-DD",                 // required
      "startTime": "HH:MM",                 // required (24h)
      "endTime": "HH:MM",                   // required (24h)
      "price": 0.0,                         // SGD, >= 0
      "maxParticipants": 20,                // required (int > 0)
      "imageUrl": "optional"
    }
    """
    body = request.get_json(silent=True) or {}

    # Basic required fields
    required_basic = ["title", "description", "location", "date", "maxParticipants"]
    missing_basic = [f for f in required_basic if body.get(f) in (None, "", [])]
    if missing_basic:
        return jsonify({"success": False, "error": f"Missing field(s): {', '.join(missing_basic)}"}), 400

    title = str(body.get("title")).strip()
    description = str(body.get("description")).strip()
    location = str(body.get("location")).strip()
    date_str = str(body.get("date")).strip()
    imageUrl = str(body.get("imageUrl")).strip() if body.get("imageUrl") else ""

    # maxParticipants must be positive integer
    try:
        max_part = int(body.get("maxParticipants"))
        if max_part <= 0:
            raise ValueError
    except Exception:
        return jsonify({"success": False, "error": "maxParticipants must be a positive integer"}), 400

    # Validate date
    ok, date_val = validate_date(date_str)
    if not ok:
        return jsonify({"success": False, "error": date_val}), 400

    # Legacy support: category -> type, time -> startTime (2h default end)
    legacy_category = (body.get("category") or "").strip().lower()
    legacy_time = (body.get("time") or "").strip()
    if not body.get("type") and legacy_category:
        mapping = {"sports": "sports", "workshop": "workshop", "cultural": "culture", "social": "other"}
        body["type"] = mapping.get(legacy_category, "other")
    if not body.get("startTime") and legacy_time:
        body["startTime"] = legacy_time
    if body.get("startTime") and not body.get("endTime"):
        body["endTime"] = add_minutes_to_hhmm(body["startTime"], 120)

    # format
    fmt_input = body.get("format", "offline")  # default offline for legacy
    ok, fmt = validate_event_format(fmt_input)
    if not ok:
        return jsonify({"success": False, "error": fmt}), 400

    # venueType (for offline only)
    ok, venue_type = validate_event_venue_type(fmt, body.get("venueType"))
    if not ok:
        return jsonify({"success": False, "error": venue_type}), 400

    # type
    if not body.get("type"):
        return jsonify({"success": False, "error": "type is required"}), 400
    ok, ev_type = validate_event_type(body.get("type"))
    if not ok:
        return jsonify({"success": False, "error": ev_type}), 400

    # region
    if not body.get("region"):
        return jsonify({"success": False, "error": "region is required"}), 400
    ok, region = validate_event_region(body.get("region"))
    if not ok:
        return jsonify({"success": False, "error": region}), 400

    # organiser
    organiser = str(body.get("organiser") or "").strip()
    if not organiser:
        return jsonify({"success": False, "error": "organiser is required"}), 400

    # times
    ok, st = validate_hhmm_time(body.get("startTime"), "startTime")
    if not ok:
        return jsonify({"success": False, "error": st}), 400
    ok, et = validate_hhmm_time(body.get("endTime"), "endTime")
    if not ok:
        return jsonify({"success": False, "error": et}), 400

    ok, _ = ensure_start_before_end(date_val, st, et)
    if not ok:
        return jsonify({"success": False, "error": _}), 400

    # price
    ok, price = validate_price_float(body.get("price", 0))
    if not ok:
        return jsonify({"success": False, "error": price}), 400

    # derive timing
    timing = derive_timing_bucket(st)

    # Disallow creating events scheduled in the past (relative to current UTC time)
    event_dt = _combine_date_time(date_val, st)
    if not event_dt:
        return jsonify({"success": False, "error": "Invalid date/time combination"}), 400
    if event_dt <= datetime.utcnow():
        return jsonify({"success": False, "error": "Event start must be in the future"}), 400

    # Compose event doc (new schema)
    event = {
        "title": title,
        "description": description,
        "format": fmt,
        "venueType": venue_type,
        "type": ev_type,
        "region": region,
        "organiser": organiser,
        "location": location,
        "date": date_val,
        "startTime": st,
        "endTime": et,
        "timing": timing,
        "price": price,
        "imageUrl": imageUrl,
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
        return jsonify({"success": True, "eventId": ref.id, "message": "Event created successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/api/admin/events/<event_id>', methods=['PUT'])
@require_admin
def update_event(current_user, event_id: str):
    """
    Update an existing event (admin only).
    Accepts any subset of new fields:
      - title, description, format, venueType, type, region, organiser, location,
        date, startTime, endTime, price, maxParticipants, imageUrl, status
    Backward-compat:
      - category -> type mapping
      - time -> startTime (adds 2h to endTime if not provided)
    Validations:
      - enums for format/type/region/venueType
      - date/time formats and ordering (start < end)
      - event start not in the past (if date/startTime provided)
      - price >= 0
      - maxParticipants >= currentParticipants
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

    # Simple string fields
    for k in ("title", "description", "organiser", "location", "imageUrl", "status"):
        if k in body and isinstance(body[k], str):
            updates[k] = body[k].strip()

    # format
    if "format" in body:
        ok, fmt = validate_event_format(body.get("format"))
        if not ok:
            return jsonify({"success": False, "error": fmt}), 400
        updates["format"] = fmt
        # venueType may need to be reset if format becomes online
        if fmt == "online":
            updates["venueType"] = None

    # venueType (validate against effective format)
    if "venueType" in body:
        # Prefer incoming format, else current format
        eff_format = updates.get("format", current.get("format"))
        ok, vt = validate_event_venue_type(eff_format, body.get("venueType"))
        if not ok:
            return jsonify({"success": False, "error": vt}), 400
        updates["venueType"] = vt

    # type (or legacy category)
    if "type" in body:
        ok, ev_type = validate_event_type(body.get("type"))
        if not ok:
            return jsonify({"success": False, "error": ev_type}), 400
        updates["type"] = ev_type
    if "category" in body:
        mapping = {"sports": "sports", "workshop": "workshop", "cultural": "culture", "social": "other"}
        cat = str(body.get("category") or "").strip().lower()
        if cat:
            updates["type"] = mapping.get(cat, "other")

    # region
    if "region" in body:
        ok, region = validate_event_region(body.get("region"))
        if not ok:
            return jsonify({"success": False, "error": region}), 400
        updates["region"] = region

    # date + start/end times (with legacy "time" mapping)
    new_date = updates.get("date", body.get("date", current.get("date")))
    if "date" in body:
        ok, d = validate_date(body.get("date"))
        if not ok:
            return jsonify({"success": False, "error": d}), 400
        updates["date"] = d
        new_date = d

    # Map legacy 'time' to startTime when provided
    if "time" in body and "startTime" not in body:
        body["startTime"] = body.get("time")

    start_candidate = body.get("startTime")
    end_candidate = body.get("endTime")

    if start_candidate is not None:
        ok, st = validate_hhmm_time(start_candidate, "startTime")
        if not ok:
            return jsonify({"success": False, "error": st}), 400
        updates["startTime"] = st

    if end_candidate is not None:
        ok, et = validate_hhmm_time(end_candidate, "endTime")
        if not ok:
            return jsonify({"success": False, "error": et}), 400
        updates["endTime"] = et

    # If only startTime provided, default endTime to +120 minutes
    eff_start = updates.get("startTime", current.get("startTime"))
    eff_end = updates.get("endTime", current.get("endTime"))
    eff_date = updates.get("date", current.get("date"))
    if eff_start and not eff_end:
        eff_end = add_minutes_to_hhmm(eff_start, 120)
        updates["endTime"] = eff_end

    # Validate ordering and derive timing if date/start/end changed
    if ("date" in updates) or ("startTime" in updates) or ("endTime" in updates):
        ok, _ = ensure_start_before_end(eff_date, eff_start, eff_end)
        if not ok:
            return jsonify({"success": False, "error": _}), 400
        # Not in the past (if changing start)
        if ("date" in updates) or ("startTime" in updates):
            event_dt = _combine_date_time(eff_date, eff_start)
            if not event_dt:
                return jsonify({"success": False, "error": "Invalid date/time combination"}), 400
            if event_dt <= datetime.utcnow():
                return jsonify({"success": False, "error": "Event start must be in the future"}), 400
        updates["timing"] = derive_timing_bucket(eff_start)

    # price
    if "price" in body:
        ok, price = validate_price_float(body.get("price"))
        if not ok:
            return jsonify({"success": False, "error": price}), 400
        updates["price"] = price

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