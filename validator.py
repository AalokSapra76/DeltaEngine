from math import log, sqrt, exp, erf
from datetime import datetime


# ==========================================================
# NORMAL DISTRIBUTION
# ==========================================================

def N(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


# ==========================================================
# BLACK SCHOLES PRICE
# ==========================================================

def option_price(S, K, T, r, q, sigma, option_type):

    if T <= 0:
        if option_type == "CE":
            return max(0.0, S - K)
        return max(0.0, K - S)

    d1 = (
        log(S / K)
        + (r - q + 0.5 * sigma * sigma) * T
    ) / (sigma * sqrt(T))

    d2 = d1 - sigma * sqrt(T)

    if option_type == "CE":

        return (
            S * exp(-q * T) * N(d1)
            - K * exp(-r * T) * N(d2)
        )

    return (
        K * exp(-r * T) * N(-d2)
        - S * exp(-q * T) * N(-d1)
    )


# ==========================================================
# DELTA
# ==========================================================

def delta(S, K, T, r, q, sigma, option_type):

    d1 = (
        log(S / K)
        + (r - q + 0.5 * sigma * sigma) * T
    ) / (sigma * sqrt(T))

    if option_type == "CE":
        return exp(-q * T) * N(d1)

    return exp(-q * T) * (N(d1) - 1.0)


# ==========================================================
# IMPLIED VOLATILITY
# ==========================================================

def implied_volatility(
    market_price,
    S,
    K,
    T,
    r,
    q,
    option_type,
):

    low = 0.0001
    high = 5.0

    for _ in range(150):

        mid = (low + high) / 2.0

        value = option_price(
            S,
            K,
            T,
            r,
            q,
            mid,
            option_type,
        )

        if value > market_price:
            high = mid
        else:
            low = mid

    return mid


# ==========================================================
# INPUT
# ==========================================================

print()
print("=" * 55)
print("BK PRICING VALIDATOR")
print("=" * 55)
print()

spot = float(input("Underlying Spot : "))

strike = float(input("Strike : "))

option_type = input("Option Type (CE/PE) : ").upper()

premium = float(input("Option Premium : "))

expiry = input("Expiry (YYYY-MM-DD) : ")

valuation = input(
    "Valuation Date & Time (YYYY-MM-DD HH:MM) : "
)

risk = input("Risk Free Rate % [6] : ")

if risk.strip() == "":
    risk = 6

dividend = input("Dividend Yield % [0] : ")

if dividend.strip() == "":
    dividend = 0

reference_iv = input("Reference IV (optional) : ")

reference_delta = input("Reference Delta (optional) : ")

# ==========================================================
# CONVERT
# ==========================================================

expiry_dt = datetime.strptime(
    expiry + " 15:30",
    "%Y-%m-%d %H:%M"
)

valuation_dt = datetime.strptime(
    valuation,
    "%Y-%m-%d %H:%M"
)

seconds = (
    expiry_dt - valuation_dt
).total_seconds()

T = seconds / (365.0 * 24 * 60 * 60)

risk = float(risk) / 100.0

dividend = float(dividend) / 100.0

# ==========================================================
# CALCULATE
# ==========================================================

iv = implied_volatility(
    premium,
    spot,
    strike,
    T,
    risk,
    dividend,
    option_type,
)

d = delta(
    spot,
    strike,
    T,
    risk,
    dividend,
    iv,
    option_type,
)

# ==========================================================
# OUTPUT
# ==========================================================

print()
print("=" * 55)
print("RESULT")
print("=" * 55)

print(f"Calculated IV      : {iv*100:.4f}%")
print(f"Calculated Delta   : {d:.6f}")

if reference_iv.strip():

    ref = float(reference_iv)

    print(f"Reference IV       : {ref:.4f}%")

    print(
        f"Difference         : {(iv*100-ref):.4f}%"
    )

if reference_delta.strip():

    ref = float(reference_delta)

    print(f"Reference Delta    : {ref:.6f}")

    print(
        f"Difference         : {(d-ref):.6f}"
    )

print("=" * 55)