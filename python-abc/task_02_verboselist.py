#!/usr/bin/env python3
"""
This module defines the VerboseList class.
It inherits from the built-in list and prints custom notification messages
whenever elements are added or removed.
"""


class VerboseList(list):
    """A custom list subclass that logs notifications for modifications."""

    def append(self, item):
        """Adds an item to the end of the list and prints a notification."""
        super().append(item)
        print(f"Added [{item}] to the list.")

    def extend(self, x):
        """Extends the list with an iterable and prints a notification."""
        initial_length = len(self)
        super().extend(x)
        items_added = len(self) - initial_length
        print(f"Extended the list with [{items_added}] items.")

    def remove(self, item):
        """Removes the first occurrence of an item and prints a notification."""
        print(f"Removed [{item}] from the list.")
        super().remove(item)

    def pop(self, index=-1):
        """Pops an item from a given index and prints a notification.

        Args:
            index (int): The position of the item to pop. Defaults to -1.
        """
        item = self[index]
        print(f"Popped [{item}] from the list.")
        return super().pop(index)
