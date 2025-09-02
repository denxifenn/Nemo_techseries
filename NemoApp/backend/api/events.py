from flask import Blueprint, jsonify, request

# Skeleton Events Blueprint (MVP stub)
# This file provides placeholder routes so the server can start and the frontend can integrate.
# TODO: Wire up Firestore reads/writes in subsequent steps.

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events', methods=['GET'])
def list_events():
    """
    List events (stub).
    Query params (future): category, status, limit, cursor
    """
    return jsonify({
        "success": True,
        "events": [],
        "message": "Events list stub - to be implemented with Firestore"
    }), 200

@events_bp.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id: str):
    """
    Get event details by ID (stub).
    """
    return jsonify({
        "success": True,
        "event": {"id": event_id},
        "message": "Event details stub - to be implemented with Firestore"
    }), 200