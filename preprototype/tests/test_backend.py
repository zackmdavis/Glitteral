import sys
sys.path.insert(0, '..')

import unittest

from backend import condescend_to_ascii  # it's a medical condition


class CondescensionTestCase(unittest.TestCase):
    def test_condescend_to_ascii(self):
        self.assertEqual(condescend_to_ascii("really?!"),
                         "really_question__bang_")
