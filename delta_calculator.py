from math import log, sqrt
from datetime import datetime

from scipy.stats import norm
from scipy.optimize import brentq


# ----------------------------------------------------------
# BLACK-SCHOLES CALL PRICE
# ----------------------------------------------------------

def bs_call_price(S, K, T, r, sigma):

    d1 = (
        log(S / K)
        + (r + 0.5 * sigma ** 2) * T
    ) / (sigma * sqrt(T))

    d2 = d1 - sigma * sqrt(T)

    return (
        S * norm.cdf(d1)
        - K * pow(2.718281828459045, -r * T) * norm.cdf(d2)
    )


# ----------------------------------------------------------
# BLACK-SCHOLES PUT PRICE
# ----------------------------------------------------------

def bs_put_price(S, K, T, r, sigma):

    d1 = (
        log(S / K)
        + (r + 0.5 * sigma ** 2) * T
    ) / (sigma * sqrt(T))

    d2 = d1 - sigma * sqrt(T)

    return (
        K * pow(2.718281828459045, -r * T) * norm.cdf(-d2)
        - S * norm.cdf(-d1)
    )


# ----------------------------------------------------------
# IMPLIED VOLATILITY
# ----------------------------------------------------------

def implied_volatility(price, S, K, T, r, option_type):

    if option_type == "CE":

        f = lambda sigma: bs_call_price(
            S, K, T, r, sigma
        ) - price

    else:

        f = lambda sigma: bs_put_price(
            S, K, T, r, sigma
        ) - price

    return brentq(f, 0.0001, 5.0)


# ----------------------------------------------------------
# DELTA
# ----------------------------------------------------------

def delta(S, K, T, r, sigma, option_type):

    d1 = (
        log(S / K)
        + (r + 0.5 * sigma ** 2) * T
    ) / (sigma * sqrt(T))

    if option_type == "CE":
        return norm.cdf(d1)

    return norm.cdf(d1) - 1.0


# ----------------------------------------------------------
# INPUTS
# ----------------------------------------------------------

print("\nBK DELTA CALCULATOR\n")

spot = float(input("Spot : "))
strike = float(input("Strike : "))
premium = float(input("Premium : "))
option_type = input("Option Type (CE/PE) : ").upper()

risk = float(input("Risk Free Rate (%) : ")) / 100

expiry = input("Expiry (YYYY-MM-DD) : ")
valuation = input("Valuation (YYYY-MM-DD HH:MM) : ")

expiry_dt = datetime.strptime(
    expiry + " 15:30",
    "%Y-%m-%d %H:%M"
)

valuation_dt = datetime.strptime(
    valuation,
    "%Y-%m-%d %H:%M"
)

T = (
    expiry_dt - valuation_dt
).total_seconds() / (
    365 * 24 * 60 * 60
)

# ----------------------------------------------------------
# CALCULATE
# ----------------------------------------------------------

sigma = implied_volatility(
    premium,
    spot,
    strike,
    T,
    risk,
    option_type,
)

d = delta(
    spot,
    strike,
    T,
    risk,
    sigma,
    option_type,
)

# ----------------------------------------------------------
# OUTPUT
# ----------------------------------------------------------

print("\n-----------------------------")
print(f"Calculated IV     : {sigma*100:.4f}%")
print(f"Calculated Delta  : {d:.6f}")
print("-----------------------------")