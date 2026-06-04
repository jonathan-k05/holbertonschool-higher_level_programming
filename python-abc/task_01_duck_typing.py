#!/usr/bin/env python3
"""
This module demonstrates Abstract Base Classes (ABCs) and Duck Typing.
It defines a Shape interface, concrete Circle and Rectangle implementations,
and a standalone function to process them polymorphically.
"""
from abc import ABC, abstractmethod
import math


class Shape(ABC):
    """Abstract base class that acts as a blueprint for geometric shapes."""

    @abstractmethod
    def area(self):
        """Calculates the area of the shape."""
        pass

    @abstractmethod
    def perimeter(self):
        """Calculates the perimeter of the shape."""
        pass


class Circle(Shape):
    """Concrete implementation of a Shape representing a circle."""

    def __init__(self, radius):
        """Initializes a Circle with a radius."""
        self.radius = abs(radius)

    def area(self):
        """Returns the area of the circle."""
        return math.pi * (self.radius ** 2)

    def perimeter(self):
        """Returns the perimeter of the circle."""
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    """Concrete implementation of a Shape representing a rectangle."""

    def __init__(self, width, height):
        """Initializes a Rectangle with width and height."""
        self.width = abs(width)
        self.height = abs(height)

    def area(self):
        """Returns the area of the rectangle."""
        return self.width * self.height

    def perimeter(self):
        """Returns the perimeter of the rectangle."""
        return 2 * (self.width + self.height)


def shape_info(shape):
    """Prints the area and perimeter of a shape using duck typing."""
    print(f"Area: {shape.area()}")
    print(f"Perimeter: {shape.perimeter()}")
