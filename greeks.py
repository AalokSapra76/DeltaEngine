# greeks.py

"""
Black-Scholes Greeks Calculator
"""

from math import log, sqrt, exp
from scipy.stats import norm


class Greeks:

    @staticmethod
    def delta(
        spot: float,
        strike: float,
        iv: float,
        days_to_expiry: float,
        option_type: str,
        risk_free_rate: float = 0.06
    ) -> float:

        if iv <= 0:
            return 0.0

        T = max(days_to_expiry / 365.0, 1e-8)

        sigma = iv / 100.0

        d1 = (
            log(spot / strike)
            + (risk_free_rate + 0.5 * sigma ** 2) * T
        ) / (sigma * sqrt(T))

        if option_type.upper() == "CE":
            return norm.cdf(d1)

        return norm.cdf(d1) - 1

    @staticmethod
    def gamma(
        spot: float,
        strike: float,
        iv: float,
        days_to_expiry: float,
        risk_free_rate: float = 0.06
    ) -> float:

        if iv <= 0:
            return 0.0

        T = max(days_to_expiry / 365.0, 1e-8)

        sigma = iv / 100.0

        d1 = (
            log(spot / strike)
            + (risk_free_rate + 0.5 * sigma ** 2) * T
        ) / (sigma * sqrt(T))

        return (
            norm.pdf(d1)
            /
            (
                spot
                * sigma
                * sqrt(T)
            )
        )

    @staticmethod
    def theta(
        spot: float,
        strike: float,
        iv: float,
        days_to_expiry: float,
        option_type: str,
        risk_free_rate: float = 0.06
    ):

        if iv <= 0:
            return 0.0

        T = max(days_to_expiry / 365.0, 1e-8)

        sigma = iv / 100.0

        d1 = (
            log(spot / strike)
            + (risk_free_rate + 0.5 * sigma ** 2) * T
        ) / (sigma * sqrt(T))

        d2 = d1 - sigma * sqrt(T)

        first = (
            -spot
            * norm.pdf(d1)
            * sigma
            /
            (2 * sqrt(T))
        )

        if option_type.upper() == "CE":

            second = (
                risk_free_rate
                * strike
                * exp(-risk_free_rate * T)
                * norm.cdf(d2)
            )

            return (first - second) / 365

        second = (
            risk_free_rate
            * strike
            * exp(-risk_free_rate * T)
            * norm.cdf(-d2)
        )

        return (first + second) / 365