import sys
import os
import unittest
from temperature import celsius_to_fahrenheit, fahrenheit_to_celsius

# Walk through all directories starting from the project root and add them to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

# Walk through all directories under root_path and add them to sys.path
for dirpath, dirnames, filenames in os.walk(root_path):
    sys.path.append(dirpath)

class TestTemperatureConversion(unittest.TestCase):

    def test_celsius_to_fahrenheit(self):
        # Test normal cases
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40)
        
        # Test edge cases
        self.assertAlmostEqual(celsius_to_fahrenheit(-273.15), -459.67)  # Absolute zero
        self.assertAlmostEqual(celsius_to_fahrenheit(56.7), 134.06)  # Random float

    def test_fahrenheit_to_celsius(self):
        # Test normal cases
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)
        self.assertAlmostEqual(fahrenheit_to_celsius(-40), -40)
        
        # Test edge cases
        self.assertAlmostEqual(fahrenheit_to_celsius(-459.67), -273.15)  # Absolute zero
        self.assertAlmostEqual(fahrenheit_to_celsius(134.06), 56.7)  # Random float

    def test_inverse_conversion(self):
        # Test if converting back and forth gives the original value
        celsius_values = [0, 100, -40, 56.7, -273.15]
        for c in celsius_values:
            f = celsius_to_fahrenheit(c)
            self.assertAlmostEqual(fahrenheit_to_celsius(f), c)

        fahrenheit_values = [32, 212, -40, 134.06, -459.67]
        for f in fahrenheit_values:
            c = fahrenheit_to_celsius(f)
            self.assertAlmostEqual(celsius_to_fahrenheit(c), f)

if __name__ == '__main__':
    unittest.main()