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
        }
        for token, tokenclass in legitimates.items():
            with self.subTest(token=token):
                self.assertTrue(tokenclass.match(token))
                for mismatching_tokenclass in (
                        set(legitimates.values()) - {tokenclass}):
                    self.assertIsNone(mismatching_tokenclass.match(token))

class TokenizerTest(unittest.TestCase):

    def test_tokenize_codeform(self):
        self.assertEqual(
            Tokenizer().tokenize("(foo 'bar' \"quux\" 3)"),
            [OpenParenthesis("("), Identifier("foo"),
             InternLiteral("'bar'"), StringLiteral('"quux"'),
             IntegerLiteral("3"), CloseParenthesis(")")]
        )

if __name__ == "__main__":
    unittest.main()
