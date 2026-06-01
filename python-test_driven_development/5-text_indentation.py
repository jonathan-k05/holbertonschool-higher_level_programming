#!/usr/bin/python3
"""
This module provides a function for text indentation.
It adds two newlines after each '.', '?' or ':' character.
Raises TypeError if the argument is not a string.
"""


def text_indentation(text):
    """
    Prints text with 2 new lines after each '.', '?' or ':'.
    Raises TypeError if text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    line = ""
    for char in text:
        if char in [".", "?", ":"]:
            print(line.strip())
            print()
            line = ""
        else:
            line += char
    if line.strip():
        print(line.strip(), end="")
