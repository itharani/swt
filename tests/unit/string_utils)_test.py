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
        # Test with a regular string
        self.assertEqual(reverse_string("hello"), "olleh")
        # Test with an empty string
        self.assertEqual(reverse_string(""), "")
        # Test with a single character
        self.assertEqual(reverse_string("a"), "a")
        # Test with a palindrome
        self.assertEqual(reverse_string("madam"), "madam")
        # Test with spaces
        self.assertEqual(reverse_string("a b c"), "c b a")
        # Test with special characters
        self.assertEqual(reverse_string("!@#"), "#@!")

    def test_capitalize_string(self):
        # Test with a regular string
        self.assertEqual(capitalize_string("hello"), "Hello")
        # Test with an empty string
        self.assertEqual(capitalize_string(""), "")
        # Test with a single lowercase character
        self.assertEqual(capitalize_string("a"), "A")
        # Test with a single uppercase character
        self.assertEqual(capitalize_string("A"), "A")
        # Test with already capitalized string
        self.assertEqual(capitalize_string("Hello"), "Hello")
        # Test with all uppercase string
        self.assertEqual(capitalize_string("HELLO"), "Hello")
        # Test with special characters
        self.assertEqual(capitalize_string("!hello"), "!hello")

    def test_count_vowels(self):
        # Test with a regular string
        self.assertEqual(count_vowels("hello"), 2)
        # Test with an empty string
        self.assertEqual(count_vowels(""), 0)
        # Test with no vowels
        self.assertEqual(count_vowels("bcdfg"), 0)
        # Test with all vowels
        self.assertEqual(count_vowels("aeiouAEIOU"), 10)
        # Test with mixed case
        self.assertEqual(count_vowels("HeLLo"), 2)
        # Test with special characters
        self.assertEqual(count_vowels("h@ll0"), 0)

    def test_is_palindrome(self):
        # Test with a palindrome
        self.assertTrue(is_palindrome("madam"))
        # Test with a non-palindrome
        self.assertFalse(is_palindrome("hello"))
        # Test with an empty string
        self.assertTrue(is_palindrome(""))
        # Test with a single character
        self.assertTrue(is_palindrome("a"))
        # Test with spaces
        self.assertTrue(is_palindrome('a b a'))
        # Test with special characters
        self.assertTrue(is_palindrome("!@#!@#"))
        # Test with mixed case palindrome
        self.assertTrue(is_palindrome("Madam"))

if __name__ == '__main__':
    unittest.main()