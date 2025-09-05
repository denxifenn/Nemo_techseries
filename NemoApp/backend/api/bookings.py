from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db
from firebase_admin import firestore as admin_fs
from datetime import datetime, timedelta

bookings_bp = Blueprint('bookings', __name__)

def _combine_date_time(date_str: str, time_str: str):
    """Combine 'YYYY-MM-DD' and 'HH:MM' to a naive UTC datetime."""
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except Exception:
        return None

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

    Query:
      - filter: "current" | "past" | "all" (default "current")
        * current: upcoming events (start >= now) and not cancelled
        * past: events already started (start < now) OR cancelled bookings
        * all: no filtering
    """
    try:
        filter_val = (request.args.get('filter') or 'current').strip().lower()
        now = datetime.utcnow()

        my = []
        q = db.collection('bookings').where('userId', '==', current_user)
        for doc in q.stream():
            booking = doc.to_dict()
            booking['id'] = doc.id

            # Attach event summary if available and compute isPast
            ev_id = booking.get('eventId')
            is_past = False
            if ev_id:
                ev_snap = db.collection('events').document(ev_id).get()
                if ev_snap.exists:
                    ev = ev_snap.to_dict()
                    booking['event'] = {
                        'id': ev_snap.id,
                        'title': ev.get('title'),
                        'date': ev.get('date'),
                        'startTime': ev.get('startTime') or ev.get('time'),
                        'location': ev.get('location'),
                        'type': ev.get('type') or ev.get('category')
                    }
                    event_dt = _combine_date_time(ev.get('date') or '', (ev.get('startTime') or ev.get('time') or ''))
                    if event_dt:
                        is_past = event_dt < now

            status = (booking.get('status') or '').lower()
            include = True
            if filter_val == 'current':
                include = (status != 'cancelled') and (not is_past)
            elif filter_val == 'past':
                include = is_past or (status == 'cancelled')
            else:
                include = True

            if include:
                my.append(booking)

        return jsonify({'success': True, 'bookings': my, 'count': len(my)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bookings_bp.route('/api/bookings/<booking_id>', methods=['DELETE'])
@require_auth
def cancel_booking(current_user, booking_id: str):
    """
    Cancel the caller's booking (individual or group).
    Rules:
      - Only booking owner (userId) can cancel
      - Booking must be in 'confirmed' status
      - Cannot cancel within 24 hours before event start
    Effects:
      - Update booking.status to 'cancelled' (with cancelledAt)
      - Decrement event.currentParticipants accordingly
      - Remove user from event.participants if present
      - Remove guestEntries added by this booking's initiator (for listed names)
    """
    try:
        # Load booking
        b_ref = db.collection('bookings').document(booking_id)
        b_snap = b_ref.get()
        if not b_snap.exists:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        booking = b_snap.to_dict() or {}

        if booking.get('userId') != current_user:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        if (booking.get('status') or '').lower() != 'confirmed':
            return jsonify({'success': False, 'error': 'Only confirmed bookings can be cancelled'}), 400

        ev_id = booking.get('eventId')
        if not ev_id:
            return jsonify({'success': False, 'error': 'Invalid booking: missing eventId'}), 400

        e_ref = db.collection('events').document(ev_id)
        e_snap = e_ref.get()
        if not e_snap.exists:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        event = e_snap.to_dict() or {}
        event_dt = _combine_date_time(event.get('date') or '', (event.get('startTime') or event.get('time') or ''))
        if not event_dt:
            return jsonify({'success': False, 'error': 'Invalid event date/time'}), 400

        if event_dt - datetime.utcnow() < timedelta(days=1):
            return jsonify({'success': False, 'error': 'Cannot cancel within 24 hours of event start'}), 400

        # Transaction to update booking and event atomically
        transaction = db.transaction()

        @admin_fs.transactional
        def _txn_cancel(txn):
            e_snap_txn = e_ref.get(transaction=txn)
            if not e_snap_txn.exists:
                raise ValueError('Event not found')
            e_cur = e_snap_txn.to_dict() or {}
            participants = set(e_cur.get('participants', []))

            dec = 0
            # Remove user seat if present
            if current_user in participants:
                dec += 1

            # If group booking: remove guest entries by initiator and count them
            guest_names = booking.get('guestNames') or []
            if isinstance(guest_names, list) and guest_names:
                # ArrayRemove payload must match elements exactly
                remove_entries = [{'name': n, 'addedBy': current_user} for n in guest_names]
                txn.update(e_ref, {
                    'guestEntries': admin_fs.ArrayRemove(remove_entries)
                })
                dec += len(guest_names)

            # Build event update
            ev_update = {}
            if dec > 0:
                ev_update['currentParticipants'] = admin_fs.Increment(-dec)
            if current_user in participants:
                ev_update['participants'] = admin_fs.ArrayRemove([current_user])
            if ev_update:
                txn.update(e_ref, ev_update)

            # Mark booking cancelled
            txn.update(b_ref, {'status': 'cancelled', 'cancelledAt': admin_fs.SERVER_TIMESTAMP})

            return dec

        freed = _txn_cancel(transaction)
        return jsonify({'success': True, 'message': 'Booking cancelled', 'seatsFreed': freed}), 200

    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bookings_bp.route('/api/bookings/by-event/<event_id>', methods=['DELETE'])
@require_auth
def cancel_booking_by_event(current_user, event_id: str):
    """
    Convenience endpoint to cancel the caller's booking for a given event_id.
    Rules:
      - Only booking owner (userId) can cancel
      - Booking must be in 'confirmed' status
      - Cannot cancel within 24 hours before event start
    Effects:
      - Update booking.status to 'cancelled' (with cancelledAt)
      - Decrement event.currentParticipants accordingly
      - Remove user from event.participants if present
      - Remove guestEntries added by this booking's initiator (for listed names)
    """
    try:
        # Find the user's confirmed booking for this event
        matches = list(
            db.collection('bookings')
              .where('userId', '==', current_user)
              .where('eventId', '==', event_id)
              .where('status', '==', 'confirmed')
              .limit(1)
              .stream()
        )
        if not matches:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        b_snap = matches[0]
        b_ref = db.collection('bookings').document(b_snap.id)
        booking = b_snap.to_dict() or {}

        # Load event
        e_ref = db.collection('events').document(event_id)
        e_snap = e_ref.get()
        if not e_snap.exists:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        event = e_snap.to_dict() or {}
        event_dt = _combine_date_time(event.get('date') or '', (event.get('startTime') or event.get('time') or ''))
        if not event_dt:
            return jsonify({'success': False, 'error': 'Invalid event date/time'}), 400
        if event_dt - datetime.utcnow() < timedelta(days=1):
            return jsonify({'success': False, 'error': 'Cannot cancel within 24 hours of event start'}), 400

        # Transaction to update booking and event atomically
        transaction = db.transaction()

        @admin_fs.transactional
        def _txn_cancel(txn):
            e_snap_txn = e_ref.get(transaction=txn)
            if not e_snap_txn.exists:
                raise ValueError('Event not found')
            e_cur = e_snap_txn.to_dict() or {}
            participants = set(e_cur.get('participants', []))

            dec = 0
            # Remove user seat if present
            if current_user in participants:
                dec += 1

            # If group booking: remove guest entries by initiator and count them
            guest_names = booking.get('guestNames') or []
            if isinstance(guest_names, list) and guest_names:
                # ArrayRemove payload must match elements exactly
                remove_entries = [{'name': n, 'addedBy': current_user} for n in guest_names]
                txn.update(e_ref, {'guestEntries': admin_fs.ArrayRemove(remove_entries)})
                dec += len(guest_names)

            # Build event update
            ev_update = {}
            if dec > 0:
                ev_update['currentParticipants'] = admin_fs.Increment(-dec)
            if current_user in participants:
                ev_update['participants'] = admin_fs.ArrayRemove([current_user])
            if ev_update:
                txn.update(e_ref, ev_update)

            # Mark booking cancelled
            txn.update(b_ref, {'status': 'cancelled', 'cancelledAt': admin_fs.SERVER_TIMESTAMP})
            return dec

        freed = _txn_cancel(transaction)
        return jsonify({'success': True, 'message': 'Booking cancelled', 'seatsFreed': freed, 'bookingId': b_snap.id}), 200

    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500