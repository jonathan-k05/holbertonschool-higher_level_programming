#!/usr/bin/python3
"""
This module defines a Square class.
It serves as an introduction to private instance attributes.
"""


class Square:
    """A class that defines a square by its size."""

    def __init__(self, size):
        """Initializes a new Square instance.

        Args:
            size: The length of a side of the square.
        """
        self.__size = size
