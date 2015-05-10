import sys
sys.path.append('..')

import unittest

from lexer import *  # I know


class TokenClassMatchingTest(unittest.TestCase):

    def test_token_matching(self):
        legitimates = {
            "robot": Identifier,
            '"romance"': StringLiteral,
            "'rocketry'": InternLiteral,
            "2015": IntegerLiteral,
            "^int": IntegerSpecifer
        }
        for token, tokenclass in legitimates.items():
            with self.subTest(token=token):
                self.assertTrue(tokenclass.match(token))
                for mismatching_tokenclass in (
                        set(legitimates.values()) - {tokenclass}):
                    self.assertIsNone(mismatching_tokenclass.match(token))

class LexerTest(unittest.TestCase):

    def test_tokenize_codeform(self):
        self.assertEqual(
            Lexer().tokenize("(foo ^str 'bar' \"quux\" 3)"),
            [OpenParenthesis("("), Identifier("foo"),
             StringSpecifier("^str"),
             InternLiteral("'bar'"), StringLiteral('"quux"'),
             IntegerLiteral("3"), CloseParenthesis(")")]
        )

    def test_recognize_keyword(self):
        self.assertEqual(Lexer().tokenize(":="),
                         [Def(":=")])

    def test_recognize_type_specifier(self):
        self.assertEqual(Lexer().tokenize("^int"), [IntegerSpecifer("^int")])
        self.assertEqual(Lexer().tokenize("^str"), [StringSpecifier("^str")])

    def test_commentary(self):
        self.assertEqual(
            Lexer().tokenize("foo # This is a comment.\n2"),
            [Identifier("foo"), Commentary(), IntegerLiteral("2")]
        )


if __name__ == "__main__":
    unittest.main()
