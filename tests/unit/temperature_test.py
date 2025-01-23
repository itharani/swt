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
        # Test normal values
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40)  # Edge case where both scales are equal

        # Test fractional values
        self.assertAlmostEqual(celsius_to_fahrenheit(37.5), 99.5)
        self.assertAlmostEqual(celsius_to_fahrenheit(-17.7778), 0, places=4)  # Close to freezing point in Fahrenheit

        # Test large values
        self.assertAlmostEqual(celsius_to_fahrenheit(1000), 1832)
        self.assertAlmostEqual(celsius_to_fahrenheit(-273.15), -459.67, places=2)  # Absolute zero in Celsius

    def test_fahrenheit_to_celsius(self):
        # Test normal values
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)
        self.assertAlmostEqual(fahrenheit_to_celsius(-40), -40)  # Edge case where both scales are equal

        # Test fractional values
        self.assertAlmostEqual(fahrenheit_to_celsius(99.5), 37.5)
        self.assertAlmostEqual(fahrenheit_to_celsius(0), -17.7778, places=4)  # Close to freezing point in Celsius

        # Test large values
        self.assertAlmostEqual(fahrenheit_to_celsius(1832), 1000)
        self.assertAlmostEqual(fahrenheit_to_celsius(-459.67), -273.15, places=2)  # Absolute zero in Fahrenheit

if __name__ == '__main__':
    unittest.main()