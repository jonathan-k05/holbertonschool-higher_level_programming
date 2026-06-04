#!/usr/bin/env python3
"""Abstract Shape class with Circle and Rectangle implementations."""

import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """Abstract base class for all shapes."""

    @abstractmethod
    def area(self):
        """Return the area of the shape."""
        pass

    @abstractmethod
    def perimeter(self):
        """Return the perimeter of the shape."""
        pass


class Circle(Shape):
    """A circle defined by its radius. Negative radius is treated as its absolute value."""

    def __init__(self, radius):
        self.radius = abs(radius)

    def area(self):
        """Return π * r²."""
        return math.pi * self.radius ** 2

    def perimeter(self):
        """Return 2 * π * r."""
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    """A rectangle defined by its width and height."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        """Return width * height."""
        return self.width * self.height

    def perimeter(self):
        """Return 2 * (width + height)."""
        return 2 * (self.width + self.height)


def shape_info(shape):
    """Print the area and perimeter of any Shape (duck typing — no isinstance check)."""
    print(f"Area: {shape.area()}")
    print(f"Perimeter: {shape.perimeter()}")
