from flask import Blueprint, jsonify, request
from utils.decorators import require_auth
from services.firebase_service import db, FirebaseService
from firebase_admin import firestore as admin_fs
from utils.validators import sanitize_profile_updates, compute_profile_completion

# Profile Blueprint (MVP)
# Provides Firestore-backed profile view/update for the current user.

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get current user's profile.
    Auto-provision a minimal user document if it doesn't exist yet.
    """
    try:
        user = FirebaseService.ensure_user_doc(current_user)
        profile = {
            'uid': user.get('uid', current_user),
            'phoneNumber': user.get('phoneNumber', ''),
            'fullName': user.get('fullName', user.get('name', '')),
            'finNumber': user.get('finNumber', ''),
            'age': user.get('age'),
            'nationality': user.get('nationality', ''),
            'languages': user.get('languages', []),
            'homeCountry': user.get('homeCountry', ''),
            'restDays': user.get('restDays', []),
            'interests': user.get('interests', []),
            'skills': user.get('skills', []),
            'role': user.get('role', 'user'),
            'profilePicture': user.get('profilePicture', ''),
            'friends': user.get('friends', []),
            'profileCompleted': bool(user.get('profileCompleted', False)),
            'createdAt': user.get('createdAt'),
            'updatedAt': user.get('updatedAt'),
            'profileCompletedAt': user.get('profileCompletedAt'),
        }
        return jsonify({'success': True, 'profile': profile}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@profile_bp.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """
    Update current user's profile.

    Accepts and validates any of:
      - fullName: string (1..100)
      - age: int (18..100)
      - nationality: string (2..50)
      - languages: string[] (1..10 items)
      - homeCountry: string (2..50)
      - restDays: string[] (valid weekdays)
      - interests: string[] (<=20 items)
      - skills: { name: string(1..50), rating: "Basic"|"Proficient"|"Expert" }[]
      - profilePicture: string
    """
    try:
        body = request.get_json(silent=True) or {}

        ok, result = sanitize_profile_updates(body)
        if not ok:
            return jsonify({'success': False, 'error': result}), 400
        updates = result

        # Load current to compute completion status post-merge
        doc_ref = db.collection('users').document(current_user)
        snap = doc_ref.get()
        current = snap.to_dict() if snap.exists else {}

        merged = dict(current or {})
        merged.update(updates)

        # Compute profile completion
        is_complete, missing = compute_profile_completion(merged)

        # Server timestamps
        updates['updatedAt'] = admin_fs.SERVER_TIMESTAMP

        # Set completion flags and first-completed timestamp
        if is_complete:
            if not current or not current.get('profileCompleted'):
                updates['profileCompleted'] = True
                if not current or not current.get('profileCompletedAt'):
                    updates['profileCompletedAt'] = admin_fs.SERVER_TIMESTAMP
        else:
            # If fields removed or not yet complete, store false (idempotent)
            updates['profileCompleted'] = False

        # Persist updates
        doc_ref.set(updates, merge=True)

        # Safe response without Firestore server sentinels
        response_updates = {k: v for k, v in updates.items() if k not in ('updatedAt', 'profileCompletedAt')}

        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'updated': response_updates,
            'profileCompleted': is_complete,
            'missingFields': missing
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@profile_bp.route('/api/profile/completion-status', methods=['GET'])
@require_auth
def profile_completion_status(current_user):
    """
    Returns whether the current user's profile has all mandatory fields.
    """
    try:
        user = FirebaseService.ensure_user_doc(current_user)

        is_complete, missing = compute_profile_completion(user or {})
        required = ['phoneNumber', 'fullName', 'age', 'nationality', 'languages', 'homeCountry', 'restDays']
        completed = [f for f in required if f not in missing]
        total_required = len(required)
        total_completed = len(completed)
        pct = int(round(100 * (total_completed / total_required))) if total_required else 100

        return jsonify({
            'success': True,
            'status': {
                'profileCompleted': is_complete,
                'missingFields': missing,
                'completedFields': completed,
                'totalRequired': total_required,
                'totalCompleted': total_completed,
                'completionPercentage': pct
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500