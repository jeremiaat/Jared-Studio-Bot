from typing import Optional, Any

# Import creator config values if present
try:
    from config.config import CREATOR_USER_ID, CREATOR_USER_IDS, CREATOR_USERNAMES
except Exception:
    CREATOR_USER_ID = None
    CREATOR_USER_IDS = None
    CREATOR_USERNAMES = None

def _normalize_id_list(val) -> list[int]:
    if val is None:
        return []
    if isinstance(val, (list, tuple, set)):
        out = []
        for x in val:
            try:
                out.append(int(x))
            except Exception:
                continue
        return out
    if isinstance(val, str):
        parts = [p.strip() for p in val.split(",") if p.strip()]
        out = []
        for p in parts:
            try:
                out.append(int(p))
            except Exception:
                continue
        return out
    try:
        return [int(val)]
    except Exception:
        return []

def _normalize_username_list(val) -> list[str]:
    if not val:
        return []
    if isinstance(val, (list, tuple, set)):
        return [str(x).lstrip("@").lower() for x in val if x]
    if isinstance(val, str):
        parts = [p.strip() for p in val.split(",") if p.strip()]
        return [p.lstrip("@").lower() for p in parts]
    return [str(val).lstrip("@").lower()]

# Precompute lists used by is_creator
CREATOR_ID_LIST = _normalize_id_list(CREATOR_USER_ID) + _normalize_id_list(CREATOR_USER_IDS)
CREATOR_USERNAME_LIST = _normalize_username_list(CREATOR_USERNAMES)

def is_creator(user_or_id: Optional[Any]) -> bool:
    """
    Return True if given user object / id / username matches configured creator(s).
    Accepts:
      - telegram.User object (has .id and .username)
      - numeric id (int or numeric string)
      - username string (with or without leading @)
    """
    if user_or_id is None:
        return False

    # Try to extract id and username from a User-like object
    uid = None
    uname = None
    try:
        if hasattr(user_or_id, "id"):
            uid = int(user_or_id.id)
    except Exception:
        uid = None
    try:
        if hasattr(user_or_id, "username") and user_or_id.username:
            uname = str(user_or_id.username).lstrip("@").lower()
    except Exception:
        uname = None

    # If raw value passed (not an object), try to interpret
    if uid is None:
        try:
            uid = int(user_or_id)
        except Exception:
            uid = None

    if uname is None and isinstance(user_or_id, str) and not str(user_or_id).isdigit():
        uname = str(user_or_id).lstrip("@").lower()

    # Direct check against single CREATOR_USER_ID (if provided)
    try:
        if CREATOR_USER_ID is not None and str(CREATOR_USER_ID).strip() != "":
            try:
                if uid is not None and int(CREATOR_USER_ID) == int(uid):
                    return True
            except Exception:
                pass
    except Exception:
        pass

    # Check normalized id list
    try:
        if uid is not None and uid in CREATOR_ID_LIST:
            return True
    except Exception:
        pass

    # Check username list
    try:
        if uname and (uname in CREATOR_USERNAME_LIST):
            return True
    except Exception:
        pass

    return False