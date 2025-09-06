"""
Singapore phone utilities for phone-<>email conversion with Firebase
"""

import re

PHONE_EMAIL_DOMAIN = "phone.local"


def only_digits(s: str) -> str:
    return re.sub(r"\D+", "", str(s or ""))


def is_valid_singapore_local(local: str) -> bool:
    """
    Accept any 8-digit number as Singapore local number
    """
    d = only_digits(local)
    return bool(re.fullmatch(r"[0-9]{8}", d))


def format_singapore_phone(input_val: str) -> str:
    """
    Normalize to E.164 for Singapore: +65XXXXXXXX
    Accepts:
      - 8 digits (e.g., 91234567)
      - 65 + 8 digits (e.g., 6591234567)
      - +65 + 8 digits (e.g., +6591234567)
    """
    raw = str(input_val or "").strip()
    if not raw:
        raise ValueError("Phone required")

    digits = only_digits(raw)

    if raw.startswith("+"):
        # e.g., +6591234567
        if digits.startswith("65"):
            digits = digits[2:]
    elif digits.startswith("65") and len(digits) == 10:
        # e.g., 6591234567
        digits = digits[2:]

    if not is_valid_singapore_local(digits):
        raise ValueError("Invalid Singapore phone. Enter 8 digits.")

    return f"+65{digits}"


def phone_to_email(phone: str) -> str:
    """
    Convert E.164 phone to Firebase email alias: 6591234567@phone.local
    """
    e164 = format_singapore_phone(phone)  # +6591234567
    local = e164.replace("+", "")  # 6591234567
    return f"{local}@{PHONE_EMAIL_DOMAIN}"


def is_phone_email(email: str) -> bool:
    """
    Check if an email is in our phone-email format
    """
    s = str(email or "").strip().lower()
    return bool(re.fullmatch(r"[0-9]{10}@phone\.local", s))


def email_to_phone(email: str) -> str | None:
    """
    Convert phone-email alias back to E.164 phone
    """
    s = str(email or "").strip().lower()
    if not is_phone_email(s):
        return None
    user = s.split("@")[0]  # 6591234567
    return f"+{user}"