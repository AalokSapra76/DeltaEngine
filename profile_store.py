profiles = []


def get_profiles():
    return profiles


def add_profile(profile):
    profiles.append(profile)


def remove_profile(profile_id):

    global profiles

    before = len(profiles)

    profiles = [p for p in profiles if p["id"] != profile_id]

    return len(profiles) != before


def update_profile(profile_id, profile):

    for i, p in enumerate(profiles):

        if p["id"] == profile_id:

            profiles[i] = profile

            return True

    return False