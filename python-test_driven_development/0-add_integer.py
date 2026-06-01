#!/usr/bin/python3
"""
This module provides a function to add two integers.
It handles type validation and float-to-integer casting.
Used for integer arithmetic operations.
"""


def add_integer(a, b=98):
    """
    Adds two integers or floats (cast to int).
    Raises TypeError if a or b are not int or float.
    Returns the integer result of a + b.
    """
    if not isinstance(a, (int, float)):
        raise TypeError("a must be an integer")
    if not isinstance(b, (int, float)):
        raise TypeError("b must be an integer")

    return int(a) + int(b)
