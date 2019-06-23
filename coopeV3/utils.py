import math

def compute_price(price, a, b, c, alpha):
    if price < a:
        return price * (a + b * math.exp(-c/(price-alpha)**2))
    else:
        return price * a
