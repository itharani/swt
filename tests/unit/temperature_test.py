import sys
import os
import unittest

# Walk through all directories starting from the project root and add them to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

# Walk through all directories under root_path and add them to sys.path
for dirpath, dirnames, filenames in os.walk(root_path):
    sys.path.append(dirpath)

from temperature import celsius_to_fahrenheit, fahrenheit_to_celsius

class TestTemperatureConversions(unittest.TestCase):

    def test_celsius_to_fahrenheit(self):
        # Test normal cases
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40)  # Edge case where both scales are equal

        # Test fractional Celsius
        self.assertAlmostEqual(celsius_to_fahrenheit(37.5), 99.5)

        # Test large positive Celsius
        self.assertAlmostEqual(celsius_to_fahrenheit(1000), 1832)

        # Test large negative Celsius
        self.assertAlmostEqual(celsius_to_fahrenheit(-273.15), -459.67)  # Absolute zero

    def test_fahrenheit_to_celsius(self):
        # Test normal cases
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)
        self.assertAlmostEqual(fahrenheit_to_celsius(-40), -40)  # Edge case where both scales are equal

        # Test fractional Fahrenheit
        self.assertAlmostEqual(fahrenheit_to_celsius(99.5), 37.5)

        # Test large positive Fahrenheit
        self.assertAlmostEqual(fahrenheit_to_celsius(1832), 900)

        # Test large negative Fahrenheit
        self.assertAlmostEqual(fahrenheit_to_celsius(-459.67), -273.15)  # Absolute zero

    def test_round_trip_conversion(self):
        # Test round-trip conversion for a range of values
        for c in range(-100, 101, 10):
            f = celsius_to_fahrenheit(c)
            self.assertAlmostEqual(fahrenheit_to_celsius(f), c)

        for f in range(-148, 213, 10):
            c = fahrenheit_to_celsius(f)
            self.assertAlmostEqual(celsius_to_fahrenheit(c), f)

if __name__ == '__main__':
    unittest.main()