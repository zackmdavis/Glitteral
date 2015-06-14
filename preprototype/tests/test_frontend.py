import sys
# We want to shadow
# https://docs.python.org/3/library/parser.html with our `parser`.
sys.path.insert(0, '..')

import unittest

from lexer import lex
from parser import *
from annotator import annotate

class FrontendTestCase(unittest.TestCase):

    def test_named_function_definition(self):
        source = """
(:=λ first_plus_square_of_second |a ^int b ^int| → ^int
  (+ a (⋅ b b)))
(:= we_assert "a and b were in the fn body's env., but not here")
"""
        defn_first_plus, def_we_assert = annotate(parse(lex(source)))
        # The local environment has our arguments,
        self.assertEqual(
            Argument(IdentifierAtom('a'), TypeSpecifierAtom("^int")),
            defn_first_plus.expressions[0].local_environment['a']
        )
        # and they don't leak.
        self.assertIsNone(def_we_assert.local_environment.get('a'))

        # And we can see the defined function from the environment of
        # the subsequent expression.
        self.assertEqual(
            type(def_we_assert.environment['first_plus_square_of_second']),
            NamedFunctionDefinition
        )

    def test_definition_sets_subsequent_global_environment(self):
        source = """
(:= a [1 2 3])
(for |i a| (print_integer a))"""
        annotated = list(annotate(parse(lex(source))))
        def_a, for_i_in_a = annotated
        self.assertIsNone(def_a.global_environment.get('a'))
        self.assertEqual(
            List([IntegerAtom(1), IntegerAtom(2), IntegerAtom(3)]),
            for_i_in_a.global_environment['a']
        )

    def test_dictionary_literal_annotated_with_definition(self):
        source = """
(:= dee {"rah" 1; "hey" 2;})"""
        annotated = list(annotate(parse(lex(source))))
        def_dee, = annotated
        dictionary_literal_node = def_dee.identified
        self.assertEqual(IdentifierAtom("dee"),
                         dictionary_literal_node.identifier)
