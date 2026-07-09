"""
callback_server.py

Handles Zerodha OAuth callback.
"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from kiteconnect import KiteConnect

from token_store import TokenStore


HOST = "127.0.0.1"
PORT = 5001


class CallbackServer:

    def __init__(self, api_key, api_secret):

        self.api_key = api_key
        self.api_secret = api_secret

        self.kite = KiteConnect(api_key=api_key)

        self.token_store = TokenStore()

        self.httpd = None

    def start(self):

        parent = self

        class LoginHandler(BaseHTTPRequestHandler):

            def do_GET(self):

                parsed = urlparse(self.path)

                if parsed.path != "/login":

                    self.send_response(404)
                    self.end_headers()
                    return

                params = parse_qs(parsed.query)

                request_token = params.get("request_token", [None])[0]

                if request_token is None:

                    self.send_response(400)
                    self.end_headers()

                    self.wfile.write(
                        b"Missing request token."
                    )

                    return

                try:

                    session = parent.kite.generate_session(
                        request_token,
                        api_secret=parent.api_secret
                    )

                    access_token = session["access_token"]

                    parent.token_store.save(
                        access_token
                    )

                    self.send_response(200)
                    self.send_header(
                        "Content-Type",
                        "text/html"
                    )
                    self.end_headers()

                    self.wfile.write(
                        b"""
                        <html>
                        <body style="font-family:Arial;text-align:center;margin-top:80px;">
                        <h2>Authentication Successful</h2>
                        <p>You may close this window.</p>
                        </body>
                        </html>
                        """
                    )

                    print()
                    print("Access Token Saved.")
                    print()

                    threading.Thread(
                        target=parent.httpd.shutdown,
                        daemon=True
                    ).start()

                except Exception as e:

                    self.send_response(500)
                    self.end_headers()

                    self.wfile.write(
                        str(e).encode()
                    )

            def log_message(
                self,
                format,
                *args
            ):
                return

        self.httpd = HTTPServer(
            (HOST, PORT),
            LoginHandler
        )

        print()
        print(
            f"Waiting for Zerodha callback on http://{HOST}:{PORT}/login"
        )
        print()

        self.httpd.serve_forever()

        self.httpd.server_close()

        print("Callback Server Closed.")