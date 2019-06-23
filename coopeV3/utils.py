import math

def compute_price(price, a, b, c, alpha):
    if price < alpha:
        return float(price) * (1 + float(a) + float(b) * math.exp(-c/(price-alpha)**2))
    else:
        return price * (1 + a)
