def mask_email(email):
    """Mask email for console output"""
    if '@' in email:
        local, domain = email.split('@', 1)
        masked_local = local[:2] + '*' * (len(local) - 2) if len(local) > 2 else local
        return f"{masked_local}@{domain}"
    return email