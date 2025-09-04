import requests
from flask import Flask, Blueprint, jsonify, request
from utils.decorators import require_auth, require_admin
from services.firebase_service import db
from firebase_admin import firestore as admin_fs

app = Flask(__name__)

# Suggestions Blueprint (MVP) - Firestore-backed create/list

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/api/suggestions', methods=['POST'])
@require_auth
def create_suggestion(current_user):
    """
    Submit an event suggestion.
    Body:
    {
      "description": "Learn to cook local dishes",
    }
    Creates a 'suggestions' document with status = 'pending'.
    """
    body = request.get_json(silent=True) or {}
    title = str(body.get('title') or '').strip()
    description = str(body.get('description') or '').strip()
    category = str(body.get('category') or '').strip().lower()

    if not title or not description or not category:
        return jsonify({'success': False, 'error': 'Missing title/description/category'}), 400

    allowed = {'sports', 'workshop', 'social'}
    if category not in allowed:
        return jsonify({'success': False, 'error': f'Invalid category. Allowed: {", ".join(sorted(allowed))}'}), 400

    doc = {
        'userId': current_user,
        'eventTitle': title,
        'eventDescription': description,
        'category': category,
        'status': 'pending',
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

        # Retrieve all suggestions ordered by `createdAt`
        suggestions = db.collection('suggestions').order_by('createdAt', direction=admin_fs.Query.DESCENDING).stream()
        
        # Iterate over suggestions and append user data
        for doc in suggestions:
            s = doc.to_dict() or {}

            # Attach user display info if available
            uid = s.get('userId')
            if uid:
                user_snap = db.collection('users').document(uid).get()
                if user_snap.exists:
                    u = user_snap.to_dict() or {}
                    s['user'] = {
                        'uid': uid,
                        'name': u.get('name'),
                        'email': u.get('email')
                    }
                else:
                    s['user'] = {'error': 'User data not found'}

            out.append(s)

        return jsonify({'success': True, 'suggestions': out, 'count': len(out)}), 200
    except requests.exceptions.RequestException as e:
            return jsonify({'error': f'API request failed: {e}'}), 500
    