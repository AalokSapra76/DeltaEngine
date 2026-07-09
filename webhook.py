# webhook.py

"""
Webhook sender with persistent logging.
"""

import requests
from datetime import datetime


class Webhook:

    def __init__(self, webhook_url=None):

        self.webhook_url = (
            webhook_url
            if webhook_url
            else "https://webhookreceiver-ps6nryst2a-ey.a.run.app?key=7y7gxqhibuaqalhtgei06ns1f5ybzpdk"
        )

    # -------------------------------------------------

    def _log(self, text):

        with open("webhook_debug.log", "a") as f:

            f.write(text + "\n")

    # -------------------------------------------------

    def send(
        self,
        symbol,
        expiry,
        strike,
        option_type,
        delta,
        premium,
        spot
    ):

        payload = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "expiry": expiry,
            "strike": int(strike),
            "option_type": option_type,
            "spot": round(spot, 2),
            "premium": round(premium, 2),
            "delta": round(delta, 4)
        }

        self._log("")
        self._log("=" * 70)
        self._log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self._log("POST " + self.webhook_url)
        self._log(str(payload))

        try:

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )

            self._log(f"STATUS : {response.status_code}")
            self._log(f"REASON : {response.reason}")
            self._log("BODY:")
            self._log(response.text)

            self._log("=" * 70)

            return 200 <= response.status_code < 300

        except requests.RequestException as e:

            self._log("EXCEPTION:")
            self._log(str(e))
            self._log("=" * 70)

            return False