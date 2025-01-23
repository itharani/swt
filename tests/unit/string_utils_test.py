import sys
import os

# Walk through all directories starting from the project root and add them to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

# Walk through all directories under root_path and add them to sys.path
for dirpath, dirnames, filenames in os.walk(root_path):
    sys.path.append(dirpath)

import unittest
from string_utils import reverse_string, capitalize_string, count_vowels, is_palindrome

class TestStringUtils(unittest.TestCase):

    def test_reverse_string(self):
        # Test normal string
        self.assertEqual(reverse_string("hello"), "olleh")
        # Test empty string
        self.assertEqual(reverse_string(""), "")
        # Test single character
        self.assertEqual(reverse_string("a"), "a")
        # Test palindrome
        self.assertEqual(reverse_string("madam"), "madam")
        # Test string with spaces
        self.assertEqual(reverse_string("hello world"), "dlrow olleh")
        # Test string with special characters
        self.assertEqual(reverse_string("!@#"), "#@!")

    def test_capitalize_string(self):
        # Test normal string
        self.assertEqual(capitalize_string("hello"), "Hello")
        # Test empty string
        self.assertEqual(capitalize_string(""), "")
        # Test single character
        self.assertEqual(capitalize_string("a"), "A")
        # Test already capitalized
        self.assertEqual(capitalize_string("Hello"), "Hello")
        # Test string with spaces
        self.assertEqual(capitalize_string("hello world"), "Hello world")
        # Test string with special characters
        self.assertEqual(capitalize_string("!hello"), "!hello")

    def test_count_vowels(self):
        # Test normal string
        self.assertEqual(count_vowels("hello"), 2)
        # Test empty string
        self.assertEqual(count_vowels(""), 0)
        # Test string with no vowels
        self.assertEqual(count_vowels("bcdfg"), 0)
        # Test string with all vowels
        self.assertEqual(count_vowels("aeiou"), 5)
        # Test string with mixed case vowels
        self.assertEqual(count_vowels("AEIOUaeiou"), 10)
        # Test string with special characters
        self.assertEqual(count_vowels("h@ll0"), 10)

    def test_is_palindrome(self):
        # Test palindrome string
        self.assertTrue(is_palindrome("madam"))
        # Test non-palindrome string
        self.assertFalse(is_palindrome("hello"))
        # Test empty string
        self.assertTrue(is_palindrome(""))
        # Test single character
        self.assertTrue(is_palindrome("a"))
        # Test palindrome with spaces and punctuation
        self.assertTrue(is_palindrome("A man, a plan, a canal, Panama"))
        # Test non-palindrome with spaces and punctuation
        self.assertFalse(is_palindrome("This is not a palindrome!"))
        # Test palindrome with mixed case
        self.assertTrue(is_palindrome("RaceCar"))

if __name__ == '__main__':
    unittest.main()