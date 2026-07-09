# token_store.py

"""
Persistent access token storage for Zerodha Kite Connect.
"""

import json
import os
from datetime import datetime


class TokenStore:
    def __init__(self, filename: str = "token.json"):
        self.filename = filename

    def exists(self) -> bool:
        return os.path.exists(self.filename)

    def save(self, access_token: str) -> None:
        data = {
            "access_token": access_token,
            "saved_at": datetime.now().isoformat()
        }

        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    def load(self) -> str | None:
        if not self.exists():
            return None

        try:
            with open(self.filename, "r") as f:
                data = json.load(f)

            return data.get("access_token")

        except Exception:
            return None

    def clear(self) -> None:
        if self.exists():
            os.remove(self.filename)