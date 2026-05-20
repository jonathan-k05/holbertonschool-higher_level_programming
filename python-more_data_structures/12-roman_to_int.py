#!/usr/bin/python3
def roman_to_int(roman_string):
    if not isinstance(roman_string, str):
        return 0

    values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    result = 0
    for i in range(len(roman_string)):
        current = values[roman_string[i]]
        if i + 1 < len(roman_string):
            next_val = values[roman_string[i + 1]]
        else:
            next_val = 0

        if current < next_val:
            result -= current
        else:
            result += current

    return result
