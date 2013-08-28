import math


def _round(value, precision):
    """
    Rounds a number to specified precision
    """
    rescale = pow(10, precision)
    return math.floor(value * rescale + 0.5) / rescale


def _precision(x):
    """
    Detemines the precision of a number using the string representation
    """
    x = x.upper()

    decimal = x.find('.')
    exponent_pos = x.find('E')
    result = 0

    if exponent_pos >= 0:
        exponent = x[exponent_pos + 1:]
        x = x[:exponent_pos]
        result -= float(exponent)

    if decimal >= 0:
        result = result + len(x) - decimal
        return result

    pos = len(x) - 1
    while x[pos] == '0':
        pos -= 1
        result -= 1
        if pos <= 0:
            return 0

    return result
