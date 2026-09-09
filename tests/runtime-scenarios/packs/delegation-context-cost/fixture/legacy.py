from decimal import Decimal, ROUND_HALF_UP


def net_cents(order):
    # Round the full line amount before applying the fixed rebate.
    gross = Decimal(order['unit_price']) * order['quantity'] * 100
    return max(0, int(gross.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
               - order.get('rebate_cents', 0))
