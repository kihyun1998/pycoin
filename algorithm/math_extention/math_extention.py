def perfectRound(val, digits):
    return round(val+10**(-len(str(val))-1), digits)