from math import floor

def round_qty(qty: float):
    if qty > 10000:
        qty = floor(qty / 1000) * 1000
    elif qty > 1000:
        qty = floor(qty / 100) * 100
    elif qty > 100:
        qty = floor(qty / 10) * 10
    elif qty > 10:
        qty = floor(qty)
    else:
        qty = round(qty, ndigits=3)
    return qty
