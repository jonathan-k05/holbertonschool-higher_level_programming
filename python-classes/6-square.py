#!/usr/bin/python3
"""
This module defines a Square class.
It implements size and coordinate positioning attributes with validation,
along with geometric calculations and custom stdout rendering.
"""


class Square:
    """A class that defines a square by its size and position."""

    def __init__(self, size=0, position=(0, 0)):
        """Initializes a new Square instance.

        Args:
            size (int): The length of a side of the square. Defaults to 0.
            position (tuple): A tuple containing two positive integers.
        """
        self.size = size
        self.position = position

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

    @property
    def position(self):
        """Retrieves the position of the square."""
        return self.__position

    @position.setter
    def position(self, value):
        """Sets the position tuple with strict structure validation."""
        message = 'position must be a tuple of 2 positive integers'
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError(message)

        if not isinstance(value[0], int) or not isinstance(value[1], int):
            raise TypeError(message)

        if value[0] < 0 or value[1] < 0:
            raise TypeError(message)

        self.__position = value

    def area(self):
        """Calculates and returns the current square area."""
        return self.__size ** 2

    def my_print(self):
        """Prints the square with the # character using position offsets."""
        if self.__size == 0:
            print()
            return

        for _ in range(self.__position[1]):
            print()

        for _ in range(self.__size):
            print((' ' * self.__position[0]) + ('#' * self.__size))
