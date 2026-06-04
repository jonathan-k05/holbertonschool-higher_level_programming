#!/usr/bin/python3
"""
This module defines a Square class.
It handles geometric state, validation, area calculation, and text rendering.
"""


class Square:
    """A class that defines a square by its size."""

    def __init__(self, size=0):
        """Initializes a new Square instance.

        Args:
            size (int): The length of a side of the square. Defaults to 0.
        """
        self.size = size

    @property
    def size(self):
        """Retrieves the size of the square."""
        return self.__size

    @size.setter
    def size(self, value):
        """Sets the size of the square with type and value validation."""
        if not isinstance(value, int):
            raise TypeError('size must be an integer')
        elif value < 0:
            raise ValueError('size must be >= 0')
        else:
            self.__size = value

    def area(self):
        """Calculates and returns the current square area."""
        return self.__size ** 2

    def my_print(self):
        """Prints the square with the # character to stdout."""
        if self.__size == 0:
            print()
            return

        for _ in range(self.__size):
            print('#' * self.__size)
