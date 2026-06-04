#!/usr/bin/python3
"""
This module defines a Square class.
It provides basic geometric functionality for calculating the area of a square.
"""


class Square:
    """A class that defines a square by its size."""

    def __init__(self, size=0):
        """Initializes a new Square instance.

        Args:
            size (int): The length of a side of the square. Defaults to 0.
        """
        if not isinstance(size, int):
            raise TypeError('size must be an integer')
        elif size < 0:
            raise ValueError('size must be >= 0')
        else:
            self.__size = size

    def area(self):
        """Calculates and returns the current square area."""
        return self.__size ** 2
