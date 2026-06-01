#!/usr/bin/python3
"""
This module provides a function to print a full name.
It validates that both arguments are strings.
Raises TypeError if either argument is not a string.
"""


def say_my_name(first_name, last_name=""):
    """
    Prints 'My name is <first_name> <last_name>'.
    Raises TypeError if first_name or last_name is not a string.
    """
    if not isinstance(first_name, str):
        raise TypeError("first_name must be a string")
    if not isinstance(last_name, str):
        raise TypeError("last_name must be a string")
    print("My name is {} {}".format(first_name, last_name))
