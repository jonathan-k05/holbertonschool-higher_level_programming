#!/usr/bin/env python3
"""
This module demonstrates the concept of Abstract Base Classes (ABCs) in Python.
It defines an abstract Animal class and two concrete implementations,
Dog and Cat, which override the abstract sound method.
"""
from abc import ABC, abstractmethod


class Animal(ABC):
    """Abstract class representing an animal template."""

    @abstractmethod
    def sound(self):
        """Abstract method that must be overridden by all subclasses

        to return the specific sound the animal makes.
        """
        pass


class Dog(Animal):
    """Concrete implementation of Animal representing a dog."""

    def sound(self):
        """Returns the specific sound of a dog."""
        return "Bark"


class Cat(Animal):
    """Concrete implementation of Animal representing a cat."""

    def sound(self):
        """Returns the specific sound of a cat."""
        return "Meow"
