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
    Body: {"eventId": "...", "groupMembers": ["uid1","uid2", ...]}
    Behavior:
      - Includes current_user automatically
      - Deduplicates members
      - Adds only members not already in event participants
      - Enforces remaining capacity atomically
      - Creates one booking document representing the group booking
    """
    body = request.get_json(silent=True) or {}
    event_id = body.get('eventId')
    group_members = body.get('groupMembers', [])
    if not isinstance(group_members, list):
        group_members = []

    # Deduplicate and ensure the initiator is included
    all_members = [current_user] + group_members
    deduped = list(dict.fromkeys(all_members))  # preserve order and de-dup

    transaction = db.transaction()

    @admin_fs.transactional
    def _txn_create_group(transaction):
        event_ref, event_snap = _get_event_in_txn(transaction, event_id)
        event = event_snap.to_dict()

        max_part = int(event.get('maxParticipants', 0) or 0)
        current_part = int(event.get('currentParticipants', 0) or 0)
        participants = set(event.get('participants', []))

        # Only add members not already participating
        new_members = [uid for uid in deduped if uid not in participants]
        if len(new_members) == 0:
            raise ValueError('All provided members are already participants')

        available = max_part - current_part
        if len(new_members) > available:
            raise ValueError(f'Only {available} spots available')

        # Create group booking
        booking_ref = db.collection('bookings').document()
        booking_data = {
            'eventId': event_id,
            'userId': current_user,
            'bookingType': 'group',
            'groupMembers': deduped,  # full requested group (including initiator)
            'status': 'confirmed',
            'createdAt': admin_fs.SERVER_TIMESTAMP
        }
        transaction.set(booking_ref, booking_data)

        # Update event atomically for only the newly added members
        transaction.update(event_ref, {
            'currentParticipants': admin_fs.Increment(len(new_members)),
            'participants': admin_fs.ArrayUnion(new_members)
        })

        return booking_ref.id, len(new_members)

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