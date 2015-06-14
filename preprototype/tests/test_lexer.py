import sys
sys.path.append('..')

import unittest

from lexer import *  # I know


class TokenClassMatchingTestCase(unittest.TestCase):

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

class LexerTestCase(unittest.TestCase):

    def test_tokenize_codeform(self):
        self.assertEqual(
            Lexer().tokenize("(foo ^str 'bar' \"quux\" 3)"),
            [OpenParenthesis("("), Identifier("foo"),
             StringSpecifier("^str"),
             InternLiteral("'bar'"), StringLiteral('"quux"'),
             IntegerLiteral("3"), CloseParenthesis(")")]
        )

    def test_tokenize_dictionary(self):
        self.assertEqual(
            Lexer().tokenize('{"foo" 1; "bar" 2; "quux" 3;}'),
            [OpenBrace("{"),
             StringLiteral('"foo"'), IntegerLiteral("1"), Semicolon(";"),
             StringLiteral('"bar"'), IntegerLiteral("2"), Semicolon(";"),
             StringLiteral('"quux"'), IntegerLiteral("3"), Semicolon(";"),
             CloseBrace("}")]
        )

    def test_leading_whitespace_is_okay(self):
        Lexer().tokenize(" (foo)")

    def test_integers_in_identifiers(self):
        self.assertEqual(
            Lexer().tokenize("foo2"),
            [Identifier("foo2")]
        )
        self.assertNotEqual(
            Lexer().tokenize("2foo"),
            [Identifier("2foo")]
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

    def test_recognize_subscript_def(self):
        self.assertEqual(Lexer().tokenize('_:='), [SubscriptDef('_:=')])

    def test_recognize_type_specifier(self):
        self.assertEqual(Lexer().tokenize("^int"), [IntegerSpecifer("^int")])
        self.assertEqual(Lexer().tokenize("^str"), [StringSpecifier("^str")])
        self.assertEqual(Lexer().tokenize("^[int]"),
                         [IntegerListSpecifier("^[int]")])
        self.assertEqual(Lexer().tokenize("^[str]"),
                         [StringListSpecifier("^[str]")])

    def test_commentary(self):
        self.assertEqual(
            Lexer().tokenize("foo # This is a comment.\n2"),
            [Identifier("foo"), Commentary(), IntegerLiteral("2")]
        )

    def test_trailing_newline(self):

        self.assertEqual(
            Lexer().tokenize("2 bar\nquux"),
            [IntegerLiteral("2"), Identifier("bar"),
             Identifier("quux")]
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

class PreparsingTestCase(unittest.TestCase):

    def test_undelimitedness(self):
        our_lexer = Lexer()
        our_lexer.tokenize("(for |i (range")
        self.assertFalse(our_lexer.undelimited())
        our_lexer.tokenize("10)| i)")
        self.assertTrue(our_lexer.undelimited())

    def test_emit_indent_tokens(self):
        source = """:= a 1
   := b 2"""
        our_lexer = Lexer()
        tokens = our_lexer.tokenize(source)
        self.assertEqual(1, our_lexer.indentation_level)
        self.assertEqual(
            [
                Def(":="), Identifier("a"), IntegerLiteral("1"),
                Indent(),
                Def(":="), Identifier("b"), IntegerLiteral("2"),
            ],
            tokens
        )
        further_source = "\n      := c 3"
        subsequent_tokens = our_lexer.tokenize(further_source)
        self.assertEqual(2, our_lexer.indentation_level)
        self.assertEqual(
            [
                Indent(),
                Def(":="), Identifier("c"), IntegerLiteral("3"),
            ],
            subsequent_tokens
        )

    def test_emit_dedent_tokens(self):
        source = "\n:= d 4"
        our_lexer = Lexer()
        our_lexer.indentation_level = 1
        tokens = our_lexer.tokenize(source)
        self.assertEqual(0, our_lexer.indentation_level)
        self.assertEqual(
            [
                Dedent(), Def(":="), Identifier("d"), IntegerLiteral("4"),
            ],
            tokens
        )

    def test_consecutive_dedents(self):
        source = """
if (= a 1)—
   if (foo b)—
      (attack! c)"""
        our_lexer = Lexer()
        tokens = our_lexer.tokenize(source)
        self.assertEqual(2, our_lexer.indentation_level)
        further_source = """
(mine "minerals")
"""
        first_dedent, second_dedent, *_rest = our_lexer.tokenize(further_source)
        self.assertEqual(0, our_lexer.indentation_level)
        self.assertEqual(Dedent(), first_dedent)
        self.assertEqual(Dedent(), second_dedent)

    @unittest.skip("TODO")
    def test_only_emit_indentation_tokens_while_undelimited(self):
        return "test code should go here"


if __name__ == "__main__":
    unittest.main()
