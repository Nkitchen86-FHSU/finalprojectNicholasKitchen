# Weight conversions to grams
GRAM_CONVERSION = {
    'g': 1,
    'oz': 28.3495,
    'lb': 453.592,
}

# Volume conversions to milliliters
VOLUME_CONVERSION = {
    'fl oz': 29.5735,
    'gal': 3785.41,
    'l': 1000,
}

# Convert weight to grams. Return none if unit is unknown
def convert_to_grams(amount, unit):
    if unit in GRAM_CONVERSION:
        return amount * GRAM_CONVERSION[unit]
    return None

# Convert volume to milliliters. Return none if unit is unknown
def convert_to_ml(amount, unit):
    if unit in VOLUME_CONVERSION:
        return amount * VOLUME_CONVERSION[unit]
    return None