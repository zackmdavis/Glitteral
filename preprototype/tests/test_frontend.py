import sys
# We want to shadow
# https://docs.python.org/3/library/parser.html with our `parser`.
sys.path.insert(0, '..')

import unittest

from lexer import lex
from parser import *
from annotator import annotate

class FrontendTestCase(unittest.TestCase):

    def test_experimental_annotation_development(self):
        source = """
(:=λ first_plus_square_of_second |a ^int b ^int| → ^int
  (+ a (⋅ b b)))  # This is a comment.
"""
        expressionstream = [n for n in parse(lex(source))]
        annotated = [n for n in annotate(parse(lex(source)))]
        # from pudb import set_trace as debug; debug()
        #
        # TODO make this into a real test case instead of a mere setup
        # harness for an exploration REPL

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
