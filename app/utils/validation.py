def validate_protection_fields(protected: bool, username: str, password: str, is_update: bool, keep_existing: bool):
    """Return an error message, or None if the site-protection fields are valid."""
    if not protected:
        return None
    if not username:
        return "A username is required when password protection is enabled."
    if not password and not (is_update and keep_existing):
        return "A password is required when password protection is enabled."
    return None
