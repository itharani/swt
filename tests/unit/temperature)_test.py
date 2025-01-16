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
        # Test known values
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40)
        
        # Test edge cases
        self.assertAlmostEqual(celsius_to_fahrenheit(-273.15), -459.67)  # Absolute zero
        self.assertAlmostEqual(celsius_to_fahrenheit(1e-10), 32.00000000018)  # Very small positive number
        self.assertAlmostEqual(celsius_to_fahrenheit(-1e-10), 31.99999999982)  # Very small negative number

    def test_fahrenheit_to_celsius(self):
        # Test known values
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)
        self.assertAlmostEqual(fahrenheit_to_celsius(-40), -40)
        
        # Test edge cases
        self.assertAlmostEqual(fahrenheit_to_celsius(-459.67), -273.15)  # Absolute zero
        self.assertAlmostEqual(fahrenheit_to_celsius(1e-10), -17.77777777777778)  # Very small positive number
        self.assertAlmostEqual(fahrenheit_to_celsius(-1e-10), -17.77777777777778)  # Very small negative number

    def test_round_trip_conversion(self):
        # Test round-trip conversion for a range of values
        for c in range(-1000, 1001, 100):
            f = celsius_to_fahrenheit(c)
            self.assertAlmostEqual(fahrenheit_to_celsius(f), c, places=5)

        for f in range(-1000, 1001, 100):
            c = fahrenheit_to_celsius(f)
            self.assertAlmostEqual(celsius_to_fahrenheit(c), f, places=5)

if __name__ == '__main__':
    unittest.main()