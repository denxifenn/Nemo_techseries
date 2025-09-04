from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db
from firebase_admin import firestore as admin_fs

bookings_bp = Blueprint('bookings', __name__)

def _get_event_in_txn(transaction, event_id):
    event_ref = db.collection('events').document(event_id)
    event_snap = event_ref.get(transaction=transaction)
    if not event_snap.exists:
        raise ValueError('Event not found')
    return event_ref, event_snap

@bookings_bp.route('/api/bookings/individual', methods=['POST'])
@require_auth
def create_individual_booking(current_user):
    """
    Create an individual booking.
    Body: {"eventId": "..."}
    Behavior:
      - Prevent double booking for the same user
      - Enforce event capacity atomically via Firestore transaction
      - Update event participants and currentParticipants
      - Create a booking document
    """
    body = request.get_json(silent=True) or {}
    event_id = body.get('eventId')
    if not event_id:
        return jsonify({'success': False, 'error': 'Missing eventId'}), 400

    transaction = db.transaction()

    @admin_fs.transactional
    def _txn_create_individual(transaction):
        event_ref, event_snap = _get_event_in_txn(transaction, event_id)
        event = event_snap.to_dict()

        max_part = int(event.get('maxParticipants', 0) or 0)
        current_part = int(event.get('currentParticipants', 0) or 0)
        participants = set(event.get('participants', []))

        if current_user in participants:
            raise ValueError('User already joined this event')

        available = max_part - current_part
        if available <= 0:
            raise ValueError('Event is full')

        # Create booking
        booking_ref = db.collection('bookings').document()
        booking_data = {
            'eventId': event_id,
            'userId': current_user,
            'bookingType': 'individual',
            'groupMembers': [],
            'status': 'confirmed',
            'createdAt': admin_fs.SERVER_TIMESTAMP
        }
        transaction.set(booking_ref, booking_data)

        # Update event atomically
        transaction.update(event_ref, {
            'currentParticipants': admin_fs.Increment(1),
            'participants': admin_fs.ArrayUnion([current_user])
        })

        return booking_ref.id

    try:
        booking_id = _txn_create_individual(transaction)
        return jsonify({
            'success': True,
            'bookingId': booking_id,
            'message': 'Booking confirmed'
        }), 201
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bookings_bp.route('/api/bookings/group', methods=['POST'])
@require_auth
def create_group_booking(current_user):
    """
    Create a group booking.

    Policy update:
      - Only the initiating user (current_user) may be added as a UID.
      - Additional attendees must be provided as guest names (strings) via "groupMemberNames".
      - Any "groupMembers" UIDs provided will be ignored.
    
    Body:
      {
        "eventId": "...",
        "groupMemberNames": ["Jane Doe","Alex", ...]     # optional guest names (no account)
      }
    Behavior:
      - Always includes the initiating current_user (if not already a participant).
      - Adds guest names as seat reservations (no account), recorded on event.guestEntries.
      - Enforces remaining capacity atomically across the current_user seat (if needed) and guest names.
      - Creates one booking document representing the group booking, storing the initiator UID and guest names.
    """
    body = request.get_json(silent=True) or {}
    event_id = body.get('eventId')

    # Ignore any provided UID members per policy; only initiator UID counts
    group_members = []

    # Parse guest names (strings)
    raw_names = body.get('groupMemberNames', [])
    if not isinstance(raw_names, list):
        raw_names = []

    # Prepare initiator-only UID list
    deduped_uids = [current_user]

    # Sanitize names: trim, drop empties, de-dup case-insensitively (preserve first casing)
    seen = set()
    guest_names = []
    for n in raw_names:
        if not isinstance(n, str):
            continue
        t = n.strip()
        if not t:
            continue
        key = t.casefold()
        if key in seen:
            continue
        seen.add(key)
        guest_names.append(t)

    transaction = db.transaction()

    @admin_fs.transactional
    def _txn_create_group(transaction):
        event_ref, event_snap = _get_event_in_txn(transaction, event_id)
        event = event_snap.to_dict()

        max_part = int(event.get('maxParticipants', 0) or 0)
        current_part = int(event.get('currentParticipants', 0) or 0)
        participants = set(event.get('participants', []))

        # Compute new UIDs to actually add (initiator only)
        new_uids = [uid for uid in deduped_uids if uid not in participants]

        # Compute guest names that are not already present for this initiator
        existing_guest_keys = set()
        for ge in event.get('guestEntries', []) or []:
            try:
                name = (ge.get('name') or '').strip()
                added_by = ge.get('addedBy') or ''
                if name and added_by:
                    existing_guest_keys.add(f"{added_by}|{name.casefold()}")
            except Exception:
                # Ignore malformed guest entry records
                continue

        new_guest_names = []
        for n in guest_names:
            key = f"{current_user}|{n.casefold()}"
            if key not in existing_guest_keys:
                new_guest_names.append(n)

        # Seats requested = new UIDs + new guest names
        seats_needed = len(new_uids) + len(new_guest_names)

        if seats_needed == 0:
            # Preserve legacy message when only UIDs were provided but all are already participants
            if len(group_members) > 0 and len(new_uids) == 0:
                raise ValueError('All provided members are already participants')
            raise ValueError('No new seats requested')

        available = max_part - current_part
        if seats_needed > available:
            raise ValueError(f'Only {available} spots available')

        # Create group booking (store both uids and names)
        booking_ref = db.collection('bookings').document()
        booking_data = {
            'eventId': event_id,
            'userId': current_user,
            'bookingType': 'group',
            'groupMembers': [current_user],   # initiator only per policy
            'guestNames': guest_names,        # guest names recorded on the booking
            'status': 'confirmed',
            'createdAt': admin_fs.SERVER_TIMESTAMP
        }
        transaction.set(booking_ref, booking_data)

        # Build atomic event update
        update_data = {
            'currentParticipants': admin_fs.Increment(seats_needed)
        }
        if new_uids:
            update_data['participants'] = admin_fs.ArrayUnion(new_uids)
        if new_guest_names:
            # Store minimal guest entry (avoid SERVER_TIMESTAMP in ArrayUnion payload)
            guest_entries = [{'name': n, 'addedBy': current_user} for n in new_guest_names]
            update_data['guestEntries'] = admin_fs.ArrayUnion(guest_entries)

        transaction.update(event_ref, update_data)

        return booking_ref.id, seats_needed

    if not event_id:
        return jsonify({'success': False, 'error': 'Missing eventId'}), 400

    try:
        booking_id, joined_count = _txn_create_group(transaction)
        return jsonify({
            'success': True,
            'bookingId': booking_id,
            'joinedCount': joined_count,
            'message': f'Group booking confirmed for {joined_count} member(s) added'
        }), 201
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bookings_bp.route('/api/bookings/my', methods=['GET'])
@require_auth
def list_my_bookings(current_user):
    """
    Get current user's bookings. Also returns a minimal event summary.
    """
    try:
        my = []
        q = db.collection('bookings').where('userId', '==', current_user)
        for doc in q.stream():
            booking = doc.to_dict()
            booking['id'] = doc.id

            # Attach event summary if available
            ev_id = booking.get('eventId')
            if ev_id:
                ev_snap = db.collection('events').document(ev_id).get()
                if ev_snap.exists:
                    ev = ev_snap.to_dict()
                    booking['event'] = {
                        'id': ev_snap.id,
                        'title': ev.get('title'),
                        'date': ev.get('date'),
                        'time': ev.get('time'),
                        'location': ev.get('location'),
                        'category': ev.get('category')
                    }

            my.append(booking)

        return jsonify({'success': True, 'bookings': my, 'count': len(my)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500