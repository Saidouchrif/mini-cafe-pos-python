from typing import Any, Dict


def is_admin(user: Dict[str, Any]) -> bool:
    return user is not None and user.get("role") == "admin"
