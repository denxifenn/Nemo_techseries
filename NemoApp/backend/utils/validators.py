from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional

# Weekday constants
VALID_WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

# Skills rating constants
VALID_SKILL_RATINGS = ["Basic", "Proficient", "Expert"]


def _normalize_whitespace(s: str) -> str:
    return " ".join(str(s).split()).strip()


def _title_case_weekday(s: str) -> str:
    s = str(s or "").strip().lower()
    for wd in VALID_WEEKDAYS:
        if wd.lower() == s:
            return wd
    return s.title()


def validate_full_name(value: Any) -> Tuple[bool, Any]:
    if value is None:
        return False, "Full name is required"
    if not isinstance(value, str):
        return False, "Full name must be a string"
    v = _normalize_whitespace(value)
    if len(v) < 1 or len(v) > 100:
        return False, "Full name must be 1-100 characters"
    return True, v


def validate_age(value: Any) -> Tuple[bool, Any]:
    if value is None:
        return False, "Age is required"
    try:
        # allow numeric-like strings
        v = int(value)
    except Exception:
        return False, "Age must be an integer number"
    if v < 18 or v > 100:
        return False, "Age must be between 18 and 100"
    return True, v


def validate_nationality(value: Any) -> Tuple[bool, Any]:
    if value is None:
        return False, "Nationality is required"
    if not isinstance(value, str):
        return False, "Nationality must be a string"
    v = _normalize_whitespace(value)
    if len(v) < 2 or len(v) > 50:
        return False, "Nationality must be 2-50 characters"
    return True, v


def validate_home_country(value: Any) -> Tuple[bool, Any]:
    if value is None:
        return False, "Home country is required"
    if not isinstance(value, str):
        return False, "Home country must be a string"
    v = _normalize_whitespace(value)
    if len(v) < 2 or len(v) > 50:
        return False, "Home country must be 2-50 characters"
    return True, v


def validate_languages(value: Any) -> Tuple[bool, Any]:
    if not isinstance(value, list) or len(value) == 0:
        return False, "Languages must be a non-empty array"
    if len(value) > 10:
        return False, "Maximum 10 languages allowed"
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            return False, "Each language must be a string"
        lang = _normalize_whitespace(item)
        if len(lang) < 2 or len(lang) > 30:
            return False, f"Invalid language length: {lang}"
        key = lang.lower()
        if key not in seen:
            normalized.append(lang)
            seen.add(key)
    return True, normalized


def validate_rest_days(value: Any) -> Tuple[bool, Any]:
    if not isinstance(value, list) or len(value) == 0:
        return False, "Rest days must be a non-empty array of weekdays"
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            return False, "Each rest day must be a string"
        wd = _title_case_weekday(item)
        if wd not in VALID_WEEKDAYS:
            return False, f"Invalid weekday: {item}"
        if wd not in seen:
            normalized.append(wd)
            seen.add(wd)
    return True, normalized


def validate_interests(value: Any) -> Tuple[bool, Any]:
    if value is None:
        # treat missing as empty
        return True, []
    if not isinstance(value, list):
        return False, "Interests must be an array"
    if len(value) > 20:
        return False, "Maximum 20 interests allowed"
    normalized: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            return False, "Each interest must be a string"
        s = _normalize_whitespace(item)
        if len(s) < 1 or len(s) > 50:
            return False, f"Interest must be 1-50 characters: {s}"
        key = s.lower()
        if key not in seen:
            normalized.append(s)
            seen.add(key)
    return True, normalized


def validate_skills(value: Any) -> Tuple[bool, Any]:
    if value is None:
        # treat missing as empty
        return True, []
    if not isinstance(value, list):
        return False, "Skills must be an array"
    if len(value) > 20:
        return False, "Maximum 20 skills allowed"
    normalized: List[Dict[str, str]] = []
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            return False, "Each skill must be an object with name and rating"
        name = item.get("name")
        rating = item.get("rating")
        if not isinstance(name, str) or len(_normalize_whitespace(name)) == 0:
            return False, "Skill name must be a non-empty string"
        n = _normalize_whitespace(name)
        if len(n) > 50:
            return False, "Skill name must be at most 50 characters"
        if not isinstance(rating, str):
            return False, "Skill rating must be a string"
        r = _normalize_whitespace(rating).title()
        if r not in VALID_SKILL_RATINGS:
            return False, f"Invalid skill rating: {rating}"
        key = n.lower()
        if key not in seen:
            normalized.append({"name": n, "rating": r})
            seen.add(key)
    return True, normalized


def compute_profile_completion(profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Determine if the profile has all required fields.
    Required: phoneNumber, fullName, age, nationality, languages (non-empty), homeCountry, restDays (non-empty)
    """
    missing: List[str] = []

    def _is_non_empty_string(v: Any) -> bool:
        return isinstance(v, str) and len(_normalize_whitespace(v)) > 0

    if not _is_non_empty_string(profile.get("phoneNumber")):
        missing.append("phoneNumber")

    if not _is_non_empty_string(profile.get("fullName")):
        missing.append("fullName")

    age = profile.get("age")
    try:
        age_int = int(age) if age is not None else None
    except Exception:
        age_int = None
    if age_int is None or age_int < 18 or age_int > 100:
        missing.append("age")

    if not _is_non_empty_string(profile.get("nationality")):
        missing.append("nationality")

    langs = profile.get("languages")
    if not isinstance(langs, list) or len(langs) == 0:
        missing.append("languages")

    if not _is_non_empty_string(profile.get("homeCountry")):
        missing.append("homeCountry")

    rest = profile.get("restDays")
    if not isinstance(rest, list) or len(rest) == 0:
        missing.append("restDays")

    return (len(missing) == 0), missing


def sanitize_profile_updates(body: Dict[str, Any]) -> Tuple[bool, Dict[str, Any] or str]:
    """
    Validate and normalize incoming profile updates.
    Supports:
      - fullName, age, nationality, languages, homeCountry, restDays
      - interests, skills
      - profilePicture (string, optional)
    Returns (True, normalized_updates) or (False, error_message)
    """
    updates: Dict[str, Any] = {}

    if "fullName" in body:
        ok, v = validate_full_name(body.get("fullName"))
        if not ok:
            return False, v
        updates["fullName"] = v
        # keep legacy `name` in sync for backward compatibility
        updates["name"] = v

    if "age" in body:
        ok, v = validate_age(body.get("age"))
        if not ok:
            return False, v
        updates["age"] = v

    if "nationality" in body:
        ok, v = validate_nationality(body.get("nationality"))
        if not ok:
            return False, v
        updates["nationality"] = v

    if "languages" in body:
        ok, v = validate_languages(body.get("languages"))
        if not ok:
            return False, v
        updates["languages"] = v

    if "homeCountry" in body:
        ok, v = validate_home_country(body.get("homeCountry"))
        if not ok:
            return False, v
        updates["homeCountry"] = v

    if "restDays" in body:
        ok, v = validate_rest_days(body.get("restDays"))
        if not ok:
            return False, v
        updates["restDays"] = v

    if "interests" in body:
        ok, v = validate_interests(body.get("interests"))
        if not ok:
            return False, v
        updates["interests"] = v

    if "skills" in body:
        ok, v = validate_skills(body.get("skills"))
        if not ok:
            return False, v
        updates["skills"] = v

    # Allow updating profilePicture as a simple trimmed string
    if "profilePicture" in body:
        pp = body.get("profilePicture")
        if not isinstance(pp, str):
            return False, "profilePicture must be a string"
        updates["profilePicture"] = _normalize_whitespace(pp)

    if not updates:
        return False, "No valid fields to update"

    return True, updates

# =========================
# Event validators (schema)
# =========================

VALID_EVENT_FORMATS = ["online", "offline"]
VALID_VENUE_TYPES = ["indoor", "outdoor", "both"]
VALID_EVENT_TYPES = ["sports", "arts", "culture", "music", "performance", "workshop", "tours", "other"]
VALID_EVENT_REGIONS = ["north", "south", "east", "west", "central"]

def validate_event_format(value):
    if not isinstance(value, str):
        return False, "format must be a string"
    v = _normalize_whitespace(value).lower()
    if v not in VALID_EVENT_FORMATS:
        return False, f"format must be one of {VALID_EVENT_FORMATS}"
    return True, v

def validate_event_venue_type(event_format, value):
    # Required only when format == "offline"
    if event_format != "offline":
        return True, None
    if not isinstance(value, str):
        return False, "venueType must be a string when format is offline"
    v = _normalize_whitespace(value).lower()
    if v not in VALID_VENUE_TYPES:
        return False, f"venueType must be one of {VALID_VENUE_TYPES}"
    return True, v

def validate_event_type(value):
    if not isinstance(value, str):
        return False, "type must be a string"
    v = _normalize_whitespace(value).lower()
    if v not in VALID_EVENT_TYPES:
        return False, f"type must be one of {VALID_EVENT_TYPES}"
    return True, v

def validate_event_region(value):
    if not isinstance(value, str):
        return False, "region must be a string"
    v = _normalize_whitespace(value).lower()
    if v not in VALID_EVENT_REGIONS:
        return False, f"region must be one of {VALID_EVENT_REGIONS}"
    return True, v

def validate_date(value):
    if not isinstance(value, str):
        return False, "date must be a string in YYYY-MM-DD"
    v = _normalize_whitespace(value)
    try:
        from datetime import datetime
        datetime.strptime(v, "%Y-%m-%d")
        return True, v
    except Exception:
        return False, "Invalid date format; expected YYYY-MM-DD"

def validate_hhmm_time(value, label="time"):
    if not isinstance(value, str):
        return False, f"{label} must be a string in HH:MM"
    v = _normalize_whitespace(value)
    parts = v.split(":")
    if len(parts) != 2:
        return False, f"Invalid {label} format; expected HH:MM (24h)"
    try:
        h = int(parts[0]); m = int(parts[1])
        if h < 0 or h > 23 or m < 0 or m > 59:
            return False, f"Invalid {label} value; hour 0..23 and minute 0..59"
    except Exception:
        return False, f"Invalid {label} value; must be numeric HH:MM"
    return True, v

def derive_timing_bucket(start_time_hhmm):
    # Timing bucket definitions (SGT-based, but hh:mm classification is sufficient)
    ok, start = validate_hhmm_time(start_time_hhmm, "startTime")
    if not ok:
        return "morning"  # default fallback (should not happen after validation)
    h = int(start.split(":")[0])
    if 6 <= h <= 11:
        return "morning"
    if 12 <= h <= 17:
        return "afternoon"
    if 18 <= h <= 21:
        return "evening"
    # 22..23 or 0..5
    return "night"

def validate_price_float(value):
    try:
        p = float(value)
        if p < 0:
            return False, "price must be >= 0"
        return True, p
    except Exception:
        return False, "price must be a number"

def ensure_start_before_end(date_str, start_hhmm, end_hhmm):
    # Ensure start < end within the same day
    from datetime import datetime
    ok_d, d = validate_date(date_str)
    if not ok_d:
        return False, d
    ok_s, s = validate_hhmm_time(start_hhmm, "startTime")
    if not ok_s:
        return False, s
    ok_e, e = validate_hhmm_time(end_hhmm, "endTime")
    if not ok_e:
        return False, e
    try:
        sd = datetime.strptime(f"{d} {s}", "%Y-%m-%d %H:%M")
        ed = datetime.strptime(f"{d} {e}", "%Y-%m-%d %H:%M")
        if not (sd < ed):
            return False, "startTime must be earlier than endTime"
        return True, (d, s, e)
    except Exception:
        return False, "Invalid date/time combination"

def add_minutes_to_hhmm(hhmm, minutes):
    # Utility: return HH:MM string plus minutes
    parts = str(hhmm).split(":")
    try:
        h = int(parts[0]); m = int(parts[1])
    except Exception:
        return hhmm
    total = h * 60 + m + int(minutes)
    total %= (24 * 60)
    nh = total // 60
    nm = total % 60
    return f"{nh:02d}:{nm:02d}"