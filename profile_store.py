import json
from pathlib import Path

STORE_FILE = Path("profiles.json")


def _load_profiles():
    if not STORE_FILE.exists():
        STORE_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(STORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_profiles():
    STORE_FILE.write_text(
        json.dumps(profiles, indent=2),
        encoding="utf-8"
    )


profiles = _load_profiles()


def get_profiles():
    return profiles


def add_profile(profile):
    profiles.append(profile)
    _save_profiles()


def remove_profile(profile_id):

    global profiles

    before = len(profiles)

    profiles = [p for p in profiles if p["id"] != profile_id]

    if len(profiles) != before:
        _save_profiles()
        return True

    return False


def update_profile(profile_id, profile):

    for i, p in enumerate(profiles):

        if p["id"] == profile_id:

            profiles[i] = profile
            _save_profiles()
            return True

    return False
