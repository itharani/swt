# string_utils.py

def reverse_string(s):
    """Returns the reverse of the input string."""
    return s[::-1]

def capitalize_string(s):
    """Returns the input string with the first letter capitalized."""
    return s.capitalize()

def count_vowels(s):
    """Returns the number of vowels in the input string."""
    vowels = 'aeiouAEIOU'
    return sum(1 for char in s if char in vowels)

def is_palindrome(s):
    """Returns True if the input string is a palindrome, False otherwise."""
    cleaned_s = ''.join(char.lower() for char in s if char.isalnum())
    return cleaned_s == cleaned_s[::-1]
