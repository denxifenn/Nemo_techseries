from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db, FirebaseService
from firebase_admin import firestore as admin_fs
from utils.phone_utils import format_singapore_phone

friends_bp = Blueprint('friends', __name__)

def _get_user_by_phone(phone_number: str):
    """
    Return (uid, data) for exact phoneNumber match in Firestore.
    Accepts user input in various formats; normalizes to E.164 (+65XXXXXXXX).
    Returns (None, None) if not found or ambiguous.
    """
    try:
        normalized = format_singapore_phone(phone_number)
    except Exception:
        return None, None

    # Try Firestore users by exact phoneNumber
    try:
        results = list(
            db.collection('users')
              .where('phoneNumber', '==', normalized)
              .limit(2)
              .stream()
        )
    except Exception:
        results = []

    if len(results) == 1:
        doc = results[0]
        return doc.id, (doc.to_dict() or {})

    if len(results) > 1:
        # Ambiguous; do not guess
        return None, None

    return None, None


@friends_bp.route('/api/friends/request', methods=['POST'])
@require_auth
def send_friend_request(current_user):
    """
    Send a friend request by recipient phone number.
    Body: { "phoneNumber": "91234567" } or { "phoneNumber": "+6591234567" }
    Rules:
      - Cannot add self
      - Cannot add if already friends
      - If a pending request exists in either direction, do not duplicate
    """
    body = request.get_json(silent=True) or {}
    phone_input = (body.get('phoneNumber') or '').strip()

    if not phone_input:
        return jsonify({'success': False, 'error': 'Missing phoneNumber'}), 400

    # Normalize and resolve recipient
    try:
        normalized = format_singapore_phone(phone_input)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid Singapore phone number'}), 400

    to_uid, to_user = _get_user_by_phone(normalized)
    if not to_uid:
        return jsonify({'success': False, 'error': 'User not found for phoneNumber'}), 404

    if to_uid == current_user:
        return jsonify({'success': False, 'error': 'Cannot add yourself'}), 400

    # Get sender/recipient docs
    # Ensure sender profile exists (auto-provision if missing)
    from_user = FirebaseService.ensure_user_doc(current_user) or {}

    # Already friends?
    sender_friends = set(from_user.get('friends', []))
    if to_uid in sender_friends:
        return jsonify({'success': False, 'error': 'Already friends'}), 400

    # Check existing pending requests in either direction
    pending_a = list(
        db.collection('friendRequests')
        .where('fromUserId', '==', current_user)
        .where('toUserId', '==', to_uid)
        .where('status', '==', 'pending')
        .limit(1)
        .stream()
    )
    pending_b = list(
        db.collection('friendRequests')
        .where('fromUserId', '==', to_uid)
        .where('toUserId', '==', current_user)
        .where('status', '==', 'pending')
        .limit(1)
        .stream()
    )
    if pending_a or pending_b:
        return jsonify({'success': False, 'error': 'A pending request already exists'}), 400

    # Create request
    req_ref = db.collection('friendRequests').document()
    req_data = {
        'fromUserId': current_user,
        'toUserId': to_uid,
        'status': 'pending',
        'createdAt': admin_fs.SERVER_TIMESTAMP
    }
    req_ref.set(req_data)

    return jsonify({
        'success': True,
        'requestId': req_ref.id,
        'message': 'Friend request sent'
    }), 201


@friends_bp.route('/api/friends/request/<request_id>', methods=['PUT'])
@require_auth
def handle_friend_request(current_user, request_id: str):
    """
    Accept or reject a friend request.
    Body: { "action": "accept" | "reject" }
    Rules:
      - Only the recipient (toUserId) can accept/reject
      - On accept: add each user to the other's friends list (idempotent)
    """
    body = request.get_json(silent=True) or {}
    action = (body.get('action') or '').strip().lower()
    if action not in ('accept', 'reject'):
        return jsonify({'success': False, 'error': 'Invalid action'}), 400

    req_ref = db.collection('friendRequests').document(request_id)
    req_snap = req_ref.get()
    if not req_snap.exists:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    req = req_snap.to_dict() or {}

    if req.get('toUserId') != current_user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if req.get('status') != 'pending':
        return jsonify({'success': False, 'error': 'Request already handled'}), 400

    from_uid = req.get('fromUserId')
    to_uid = req.get('toUserId')

    if action == 'reject':
        req_ref.update({'status': 'rejected'})
        return jsonify({'success': True, 'message': 'Friend request rejected'}), 200

    # Accept: update both users' friends arrays atomically (best-effort)
    try:
        from_ref = db.collection('users').document(from_uid)
        to_ref = db.collection('users').document(to_uid)

        transaction = db.transaction()

        @admin_fs.transactional
        def _txn(txn):
            _accept_txn(txn, from_ref, to_ref, req_ref)

        _txn(transaction)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return jsonify({'success': True, 'message': 'Friend request accepted'}), 200


def _accept_txn(txn, from_ref, to_ref, req_ref):
    from_snap = from_ref.get(transaction=txn)
    to_snap = to_ref.get(transaction=txn)

    from_friends = set((from_snap.to_dict() or {}).get('friends', []))
    to_friends = set((to_snap.to_dict() or {}).get('friends', []))

    if to_ref.id not in from_friends:
        txn.update(from_ref, {'friends': admin_fs.ArrayUnion([to_ref.id])})
    if from_ref.id not in to_friends:
        txn.update(to_ref, {'friends': admin_fs.ArrayUnion([from_ref.id])})

    txn.update(req_ref, {'status': 'accepted'})


@friends_bp.route('/api/friends', methods=['GET'])
@require_auth
def list_friends(current_user):
    """
    Return user's friends with minimal profile info.
    """
    try:
        user_snap = db.collection('users').document(current_user).get()
        if not user_snap.exists:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        friend_ids = list((user_snap.to_dict() or {}).get('friends', []))
        friends = []

        # Fetch each friend (small lists are expected for MVP)
        for fid in friend_ids:
            snap = db.collection('users').document(fid).get()
            if snap.exists:
                d = snap.to_dict() or {}
                friends.append({
                    'id': fid,
                    'name': d.get('name'),
                    'phoneNumber': d.get('phoneNumber'),
                    'profilePicture': d.get('profilePicture', '')
                })

        return jsonify({'success': True, 'friends': friends, 'count': len(friends)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500