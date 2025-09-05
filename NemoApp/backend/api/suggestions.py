from flask import Blueprint, jsonify, request
from utils.decorators import require_auth, require_admin
from services.firebase_service import db
from firebase_admin import firestore as admin_fs

# Suggestions Blueprint (MVP) - Firestore-backed create/list

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/api/suggestions', methods=['POST'])
@require_auth
def create_suggestion(current_user):
    """
    Submit a free-text suggestion (no title/category/status).
    Body:
    {
      "text": "Any feedback or suggestion for future events..."
    }
    Creates a 'suggestions' document with fields: userId, text, createdAt.
    """
    body = request.get_json(silent=True) or {}
    text = str(body.get('text') or '').strip()

    if not text:
        return jsonify({'success': False, 'error': 'Missing text'}), 400
    if len(text) > 2000:
        return jsonify({'success': False, 'error': 'Text too long (max 2000 chars)'}), 400

    doc = {
        'userId': current_user,
        'text': text,
        'createdAt': admin_fs.SERVER_TIMESTAMP
    }

    try:
        ref = db.collection('suggestions').add(doc)[1]
        return jsonify({'success': True, 'suggestionId': ref.id, 'message': 'Suggestion submitted'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@suggestions_bp.route('/api/suggestions', methods=['GET'])
@require_admin
def list_suggestions(current_user):
    """
    List all suggestions (admin only).
    Returns suggestion along with basic user info if available.
    """
    try:
        out = []
        for doc in db.collection('suggestions').order_by('createdAt', direction=admin_fs.Query.DESCENDING).stream():
            s = doc.to_dict() or {}
            s['id'] = doc.id

            # Attach user display info if possible
            uid = s.get('userId')
            if uid:
                user_snap = db.collection('users').document(uid).get()
                if user_snap.exists:
                    u = user_snap.to_dict() or {}
                    s['user'] = {
                        'uid': uid,
                        'name': u.get('name'),
                        'phoneNumber': u.get('phoneNumber')
                    }

            out.append(s)

        return jsonify({'success': True, 'suggestions': out, 'count': len(out)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500