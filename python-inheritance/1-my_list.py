#!/usr/bin/python3
"""Module that defines MyList, a subclass of list."""


class MyList(list):
    """A list subclass with a print_sorted method."""

    def print_sorted(self):
        """Print the list sorted ascending, without modifying the original."""
        print(sorted(self))
