#!/usr/bin/env python3
"""
This module defines the CountedIterator class.
It wraps a standard Python iterator to keep track of the number of items
that have been successfully fetched during iteration.
"""


class CountedIterator:
    """An iterator wrapper that counts the number of items iterated over."""

    def __init__(self, some_iterable):
        """Initializes the CountedIterator with an iterable object.

        Args:
            some_iterable: Any Python iterable (e.g., list, tuple, string).
        """
        self.iterator = iter(some_iterable)
        self.counter = 0

    def get_count(self):
        """Returns the current number of items that have been fetched."""
        return self.counter

    def __iter__(self):
        """Returns the iterator object itself."""
        return self

    def __next__(self):
        """Fetches the next item from the iterator and increments the counter.

        Raises:
            StopIteration: When there are no more items left to iterate.
        """
        try:
            item = next(self.iterator)
            self.counter += 1
            return item
        except StopIteration:
            raise StopIteration
