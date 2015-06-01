import sys
sys.path.append('..')

import unittest

from utils import *  # regret nothing

class LookaheadStreamTestCase(unittest.TestCase):

    def test_lookahead_stream(self):
        stream = LookaheadStream(range(3))
        self.assertEqual(0, stream.peek())
        self.assertEqual(0, stream.pop())
        self.assertEqual(1, stream.pop())
        self.assertEqual(2, stream.peek())

if __name__ == "__main__":
    unittest.main()
