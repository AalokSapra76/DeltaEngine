# auth.py

"""
Authentication Manager

Handles

• Login URL
• Local callback server
• Access token loading
"""

from kiteconnect import KiteConnect

from token_store import TokenStore
from callback_server import CallbackServer


class AuthManager:

    def __init__(
        self,
        api_key,
        api_secret
    ):

        self.api_key = api_key
        self.api_secret = api_secret

        self.kite = KiteConnect(
            api_key=api_key
        )

        self.store = TokenStore()

    def get_access_token(self):

        token = self.store.load()

        if token:

            print("Using saved access token.")

            return token

        print()
        print("Opening Zerodha Login")
        print()

        print(
            self.kite.login_url()
        )

        print()

        server = CallbackServer(
            self.api_key,
            self.api_secret
        )

        server.start()

        token = self.store.load()

        if not token:

            raise Exception(
                "Authentication failed."
            )

        return token