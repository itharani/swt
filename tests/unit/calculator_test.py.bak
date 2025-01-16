import sys
import os
import unittest

# Walk through all directories starting from the project root and add them to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

# Walk through all directories under root_path and add them to sys.path
for dirpath, dirnames, filenames in os.walk(root_path):
    sys.path.append(dirpath)

from calculator import add, subtract, multiply, divide

class TestCalculator(unittest.TestCase):

    def test_add_positive_numbers(self):
        self.assertEqual(add(1, 2), 3)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -2), -3)

    def test_add_mixed_numbers(self):
        self.assertEqual(add(-1, 2), 1)

    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(0, 5), 5)
        self.assertEqual(add(5, 0), 5)

    def test_subtract_positive_numbers(self):
        self.assertEqual(subtract(3, 2), 1)

    def test_subtract_negative_numbers(self):
        self.assertEqual(subtract(-3, -2), -1)

    def test_subtract_mixed_numbers(self):
        self.assertEqual(subtract(-1, 2), -3)

    def test_subtract_zero(self):
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(subtract(0, 5), -5)
        self.assertEqual(subtract(5, 0), 5)

    def test_multiply_positive_numbers(self):
        self.assertEqual(multiply(3, 2), 6)

    def test_multiply_negative_numbers(self):
        self.assertEqual(multiply(-3, -2), 6)

    def test_multiply_mixed_numbers(self):
        self.assertEqual(multiply(-3, 2), -6)

    def test_multiply_zero(self):
        self.assertEqual(multiply(0, 0), 0)
        self.assertEqual(multiply(0, 5), 0)
        self.assertEqual(multiply(5, 0), 0)

    def test_divide_positive_numbers(self):
        self.assertEqual(divide(6, 2), 3)

    def test_divide_negative_numbers(self):
        self.assertEqual(divide(-6, -2), 3)

    def test_divide_mixed_numbers(self):
        self.assertEqual(divide(-6, 2), -3)

    def test_divide_by_one(self):
        self.assertEqual(divide(5, 1), 5)
        self.assertEqual(divide(-5, 1), -5)

    def test_divide_one_by_number(self):
        self.assertEqual(divide(1, 5), 0.2)
        self.assertEqual(divide(1, -5), -0.2)

    def test_divide_zero(self):
        self.assertEqual(divide(0, 5), 0)
        self.assertEqual(divide(0, -5), 0)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(5, 0)

if __name__ == '__main__':
    unittest.main()