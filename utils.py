def ensure_key(d: dict, key, default):
    """Retourne d[key], en créant la valeur par défaut si nécessaire."""
    if key not in d:
        d[key] = default
    return d[key]

LIST_UNITS_TYPES = ["pikeman", "knight", "crossbowman", "longswordsman"]
