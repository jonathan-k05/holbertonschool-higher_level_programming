#!/usr/bin/python3
"""Unittest for max_integer([..])
"""
import unittest
max_integer = __import__('6-max_integer').max_integer


class TestMaxInteger(unittest.TestCase):
    """Test cases for the max_integer function"""

    def test_regular_list(self):
        """Test with a standard list of positive integers"""
        self.assertEqual(max_integer([1, 2, 3, 4]), 4)

    def test_max_at_beginning(self):
        """Test when the max integer is at the beginning of the list"""
        self.assertEqual(max_integer([4, 3, 2, 1]), 4)

    def test_max_in_middle(self):
        """Test when the max integer is in the middle of the list"""
        self.assertEqual(max_integer([1, 3, 4, 2]), 4)

    def test_single_element(self):
        """Test with a list containing a single element"""
        self.assertEqual(max_integer([7]), 7)

    def test_empty_list(self):
        """Test with an empty list — should return None"""
        self.assertIsNone(max_integer([]))

    def test_no_argument(self):
        """Test with no argument passed (uses default empty list)"""
        self.assertIsNone(max_integer())

    def test_negative_numbers(self):
        """Test with a list of all negative integers"""
        self.assertEqual(max_integer([-1, -2, -3, -4]), -1)

    def test_mixed_positive_negative(self):
        """Test with a mix of positive and negative integers"""
        self.assertEqual(max_integer([-10, 0, 5, -3, 8, 2]), 8)

    def test_duplicate_values(self):
        """Test with a list containing duplicate integers"""
        self.assertEqual(max_integer([3, 3, 3, 3]), 3)

    def test_duplicate_max(self):
        """Test with a list where the max value appears more than once"""
        self.assertEqual(max_integer([1, 5, 3, 5, 2]), 5)

    def test_all_same_values(self):
        """Test with a list where all elements are identical"""
        self.assertEqual(max_integer([9, 9, 9]), 9)

    def test_large_numbers(self):
        """Test with very large integers"""
        self.assertEqual(max_integer([1000000, 999999, 1000001]), 1000001)

    def test_zero_in_list(self):
        """Test with zero as the maximum value"""
        self.assertEqual(max_integer([-5, -3, 0]), 0)

    def test_two_elements(self):
        """Test with a two-element list"""
        self.assertEqual(max_integer([2, 10]), 10)
        self.assertEqual(max_integer([10, 2]), 10)

    def test_unordered_list(self):
        """Test with an unordered list"""
        self.assertEqual(max_integer([3, 1, 4, 1, 5, 9, 2, 6]), 9)


if __name__ == '__main__':
    unittest.main()
