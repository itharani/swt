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

    def test_add(self):
        # Test positive numbers
        self.assertEqual(add(1, 2), 3)
        # Test negative numbers
        self.assertEqual(add(-1, -2), -3)
        # Test positive and negative number
        self.assertEqual(add(1, -2), -1)
        # Test zero
        self.assertEqual(add(0, 0), 0)
        # Test float numbers
        self.assertEqual(add(1.5, 2.5), 4.0)

    def test_subtract(self):
        # Test positive numbers
        self.assertEqual(subtract(3, 2), 1)
        # Test negative numbers
        self.assertEqual(subtract(-3, -2), -1)
        # Test positive and negative number
        self.assertEqual(subtract(3, -2), 5)
        # Test zero
        self.assertEqual(subtract(0, 0), 0)
        # Test float numbers
        self.assertEqual(subtract(3.5, 2.5), 1.0)

    def test_multiply(self):
        # Test positive numbers
        self.assertEqual(multiply(3, 2), 6)
        # Test negative numbers
        self.assertEqual(multiply(-3, -2), 6)
        # Test positive and negative number
        self.assertEqual(multiply(3, -2), -6)
        # Test zero
        self.assertEqual(multiply(0, 5), 0)
        # Test float numbers
        self.assertEqual(multiply(3.5, 2), 7.0)

    def test_divide(self):
        # Test positive numbers
        self.assertEqual(divide(6, 2), 3)
        # Test negative numbers
        self.assertEqual(divide(-6, -2), 3)
        # Test positive and negative number
        self.assertEqual(divide(6, -2), -3)
        # Test division by zero
        with self.assertRaises(ValueError):
            divide(6, 0)
        # Test float numbers
        self.assertAlmostEqual(divide(7.5, 2.5), 3.0)

if __name__ == '__main__':
    unittest.main()