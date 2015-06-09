import sys
sys.path.insert(0, '..')

import textwrap
import unittest

from unittest import mock

from backend import condescend_to_ascii, generate_associative
from parser import Dictionary, Association, StringAtom, IntegerAtom, IdentifierAtom


class CondescensionTestCase(unittest.TestCase):
    def test_condescend_to_ascii(self):
        self.assertEqual(condescend_to_ascii("really?!"),
                         "really_question__bang_")


class CodeGenerationTestCase(unittest.TestCase):
    def test_generate_associative(self):
        dictionary_node = Dictionary(
            [Association(StringAtom("bar"), IntegerAtom(4)),
             Association(StringAtom("quux"), IntegerAtom(5))]
        )
        dictionary_node.identifier = IdentifierAtom("dee")
        dictionary_node.identifier.local_environment['dee'] = mock.Mock()
        expected_code = """HashMap::new();
&mut dee.insert("bar", 4isize);
&mut dee.insert("quux", 5isize);
"""
        generated_code = generate_associative(dictionary_node)
        self.assertEqual(expected_code, generated_code)
