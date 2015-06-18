import sys
sys.path.append('..')

import random
import unittest

from string import ascii_lowercase

from utils import *  # regret nothing

class LookaheadStreamTestCase(unittest.TestCase):

    def test_lookahead_stream(self):
        stream = LookaheadStream(range(3))
        self.assertEqual(0, stream.peek())
        self.assertEqual(0, stream.pop())
        self.assertEqual(1, stream.pop())
        self.assertEqual(2, stream.peek())

class RegexOptTestCase(unittest.TestCase):

    @staticmethod
    def _random_string():
        return ''.join(random.choice(ascii_lowercase)
                       for _ in range(random.randrange(10)))

    def test_regex_opt_basic_matches(self):
        alternatives = [self._random_string() for _ in range(25)]
        our_regex = regex_opt(*alternatives)
        for this_should_match in alternatives:
            self.assertTrue(our_regex.match(this_should_match))


class PrefixesTestCase(unittest.TestCase):

    def test_prefixes(self):
        cases = [('int', ["", "i", "in", "int"]),
                 ('float', ["", "f", "fl", "flo", "floa", "float"])]
        for word, prees in cases:
            self.assertEqual(prefixes(word), prees)


if __name__ == "__main__":
    unittest.main()
