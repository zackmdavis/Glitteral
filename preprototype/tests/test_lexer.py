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
            "^int": IntegerSpecifer,
            "|": Pipe
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

    def test_recognize_booleans(self):
        for boolean in ("Truth", "Falsity"):
            self.assertEqual(
                Lexer().tokenize(boolean),
                [BooleanLiteral(boolean)]
            )

    def test_recognize_void(self):
        self.assertEqual(Lexer().tokenize("Void"), [VoidLiteral("Void")])

    def test_recognize_arrow(self):
        self.assertEqual(Lexer().tokenize('→'), [Arrow('→')])

    def test_recognize_type_specifier(self):
        self.assertEqual(Lexer().tokenize("^int"), [IntegerSpecifer("^int")])
        self.assertEqual(Lexer().tokenize("^str"), [StringSpecifier("^str")])

    def test_commentary(self):
        self.assertEqual(
            Lexer().tokenize("foo # This is a comment.\n2"),
            [Identifier("foo"), Commentary(), IntegerLiteral("2")]
        )

    def test_trailing_newline(self):
        self.assertEqual(
            Lexer().tokenize("2 bar\nquux"),
            [IntegerLiteral("2"), Identifier("bar"), Identifier("quux")]
        )

    def test_tokenize_determinate_iteration(self):
        self.assertEqual(
            Lexer().tokenize("""(for [i (range 10)] (print i))"""),
            [OpenParenthesis("("), For("for"), OpenBracket("["), Identifier("i"),
             OpenParenthesis("("), Identifier("range"), IntegerLiteral("10"),
             CloseParenthesis(")"), CloseBracket("]"), OpenParenthesis("("),
             Identifier("print"), Identifier("i"), CloseParenthesis(")"),
             CloseParenthesis(")")]
        )


if __name__ == "__main__":
    unittest.main()
