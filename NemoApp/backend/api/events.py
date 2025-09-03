from flask import Blueprint, jsonify, request
from services.firebase_service import db

# Events Blueprint with Firestore-backed listing and details
# MVP support: filter by category/status and simple limit pagination.

events_bp = Blueprint('events', __name__)

def _serialize_event(doc) -> dict:
    data = doc.to_dict()
    data['id'] = doc.id
    return data

@events_bp.route('/api/events', methods=['GET'])
def list_events():
    """
    List events with optional filtering.
    Query params:
      - category: sports|workshop|social (optional)
      - status: upcoming|completed|cancelled (optional)
      - limit: default 20, max 50
    """
    try:
        category = request.args.get('category')
        status = request.args.get('status')
        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            limit = 20
        limit = max(1, min(limit, 50))

        query = db.collection('events')

        if category:
            query = query.where('category', '==', category)
        if status:
            query = query.where('status', '==', status)

        # Simple ordering by date then time to keep results stable
        try:
            query = query.order_by('date').order_by('time')
        except Exception:
            # If 'time' does not exist on all docs, fall back to date only
            try:
                query = query.order_by('date')
            except Exception:
                # As a last resort, leave unordered (Firestore may require an order_by for cursors)
                pass

        docs = query.limit(limit).stream()
        events = [_serialize_event(d) for d in docs]

        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@events_bp.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id: str):
    """
    Get event details by ID.
    """
    try:
        ref = db.collection('events').document(event_id)
        snap = ref.get()
        if not snap.exists:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        return jsonify({
            'success': True,
            'event': _serialize_event(snap)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500