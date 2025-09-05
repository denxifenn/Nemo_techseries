from flask import Blueprint, jsonify, request
from services.firebase_service import db

# Events Blueprint with Firestore-backed listing and details
# Now supports extended fields and richer filters.

events_bp = Blueprint('events', __name__)

def _event_with_computed_fields(data: dict, include_available=True) -> dict:
    """
    Add computed fields for response:
      - availableSlots = maxParticipants - currentParticipants
      - timing: derive from startTime if missing (legacy docs)
      - startTime/endTime fallback from legacy 'time' if needed
    """
    # Legacy fallback: 'time' => 'startTime' (no endTime known)
    if 'startTime' not in data and 'time' in data and isinstance(data.get('time'), str):
        data['startTime'] = data.get('time')

    # Derive timing if missing and startTime present
    if not data.get('timing'):
        st = data.get('startTime')
        if isinstance(st, str) and len(st) >= 4 and ':' in st:
            try:
                h = int(st.split(':')[0])
                if 6 <= h <= 11:
                    data['timing'] = 'morning'
                elif 12 <= h <= 17:
                    data['timing'] = 'afternoon'
                elif 18 <= h <= 21:
                    data['timing'] = 'evening'
                else:
                    data['timing'] = 'night'
            except Exception:
                pass

    if include_available:
        try:
            max_p = int(data.get('maxParticipants') or 0)
            cur_p = int(data.get('currentParticipants') or 0)
            data['availableSlots'] = max(0, max_p - cur_p)
        except Exception:
            data['availableSlots'] = None
    return data

def _serialize_event(doc) -> dict:
    data = doc.to_dict() or {}
    data['id'] = doc.id
    return _event_with_computed_fields(data)

@events_bp.route('/api/events', methods=['GET'])
def list_events():
    """
    List events with optional filtering.
    Query params (all optional):
      - format: online|offline
      - type: sports|arts|culture|music|performance|workshop|tours|other
      - region: north|south|east|west|central
      - timing: morning|afternoon|evening|night
      - fromDate: YYYY-MM-DD (inclusive)
      - toDate: YYYY-MM-DD (inclusive)
      - minPrice: float
      - maxPrice: float
      - status: upcoming|completed|cancelled
      - category: legacy category filter for backward compatibility
      - limit: default 20, max 50
    """
    try:
        q_format = request.args.get('format')
        q_type = request.args.get('type')
        q_region = request.args.get('region')
        q_timing = request.args.get('timing')
        q_from = request.args.get('fromDate')
        q_to = request.args.get('toDate')
        q_min_price = request.args.get('minPrice')
        q_max_price = request.args.get('maxPrice')
        q_status = request.args.get('status')
        q_category = request.args.get('category')  # legacy
        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            limit = 20
        limit = max(1, min(limit, 50))

        query = db.collection('events')

        # To avoid requiring Firestore composite indexes in dev/test,
        # push at most ONE equality filter to Firestore and apply the rest in-memory.
        # Priority for server-side filter (pick first available):
        chosen_field = None
        chosen_value = None
        for field, value in (
            ('status', q_status),
            ('type', q_type),
            ('format', q_format),
            ('region', q_region),
            ('timing', q_timing),
            ('category', q_category),  # legacy
        ):
            if value:
                chosen_field, chosen_value = field, value
                break

        if chosen_field:
            try:
                query = query.where(chosen_field, '==', chosen_value)
            except Exception:
                # In case emulator/permissions cause issues, skip server-side filter
                chosen_field, chosen_value = None, None

        # Note: Apply date range in-memory to avoid composite index with other filters
        # Avoid server-side ordering to prevent composite-index requirement; we'll sort in-memory.

        docs = query.stream()
        events = [_serialize_event(d) for d in docs]

        # In-memory filters for the rest (including date range and price)
        def _passes_inmemory(e):
            # Skip the one we already applied on server
            def eq(field, qval):
                if not qval:
                    return True
                if field == chosen_field:
                    return True
                return (e.get(field) == qval)

            if not eq('format', q_format): return False
            if not eq('type', q_type): return False
            if not eq('region', q_region): return False
            if not eq('timing', q_timing): return False
            if not eq('status', q_status): return False
            if not eq('category', q_category): return False  # legacy

            # Date range (inclusive)
            d = e.get('date')
            if q_from and (not d or d < q_from): return False
            if q_to and (not d or d > q_to): return False

            return True

        events = [e for e in events if _passes_inmemory(e)]

        # Apply price range in-memory to avoid multi-field inequalities in Firestore query
        def _in_price(e):
            try:
                p = float(e.get('price') if e.get('price') is not None else 0)
            except Exception:
                return False
            if q_min_price is not None:
                try:
                    if p < float(q_min_price):
                        return False
                except Exception:
                    pass
            if q_max_price is not None:
                try:
                    if p > float(q_max_price):
                        return False
                except Exception:
                    pass
            return True

        if q_min_price is not None or q_max_price is not None:
            events = [e for e in events if _in_price(e)]

        # Secondary in-memory sort by (date, startTime/time)
        try:
            events.sort(key=lambda e: (
                (e.get('date') or ''),
                (e.get('startTime') or e.get('time') or '')
            ))
        except Exception:
            pass

        # Apply limit after in-memory filtering and sort
        events = events[:limit]
        return jsonify({'success': True, 'events': events, 'count': len(events)}), 200
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
        return jsonify({'success': True, 'event': _serialize_event(snap)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500