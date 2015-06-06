import logging
import os
import re

from collections import namedtuple

from utils import LookaheadStream

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

PartiallyMatchedSubtoken = namedtuple('PartiallyMatchedSubtoken',
                                      ('tokenclass', 'representation'))

class Token:
    def __init__(self, representation):
        self.representation = representation

    @classmethod
    def match(cls, source_fragment):
        if cls.recognizer.match(source_fragment):
            return cls(source_fragment)
        elif getattr(cls, 'prefix_recognizer',
                     re.compile('$^')).match(source_fragment):
            return PartiallyMatchedSubtoken(
                cls.__name__, source_fragment)
        else:
            return None

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.representation == other.representation)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__,
                                 self.representation)


IDENTIFIER_CHARCLASS = r"[-A-Za-z_:λ=+−⋅÷!]"

class Reserved(Token):
    ...

class Keyword(Reserved):
    ...

class If(Keyword):
    recognizer = re.compile(r"if$")

class For(Keyword):
    recognizer = re.compile(r"for$")

class Lambda(Keyword):
    recognizer = re.compile(r"λ$")

class Def(Keyword):
    recognizer = re.compile(r":=$")

class SubscriptDef(Keyword):
    recognizer = re.compile(r"_:=$")

class Deflambda(Keyword):
    recognizer = re.compile(r":=λ$")

class Arrow(Keyword):
    recognizer = re.compile(r"→$")

class Identifier(Token):
    recognizer = re.compile("{}+$".format(IDENTIFIER_CHARCLASS))


class TypeSpecifier(Reserved):
    prefix_recognizer = re.compile(r"\^{}*$".format(IDENTIFIER_CHARCLASS))

class IntegerSpecifer(TypeSpecifier):
    recognizer = re.compile(r"\^int$")

class StringSpecifier(TypeSpecifier):
    recognizer = re.compile(r"\^str$")

class OpenDelimiter(Token):
    ...

class CloseDelimiter(Token):
    ...

class SequentialDelimiter(Token):
    ...

class OpenParenthesis(OpenDelimiter):
    recognizer = re.compile(r"\($")

class CloseParenthesis(CloseDelimiter):
    recognizer = re.compile(r"\)$")

class OpenBracket(SequentialDelimiter, OpenDelimiter):
    recognizer = re.compile(r"\[$")

class CloseBracket(SequentialDelimiter, CloseDelimiter):
    recognizer = re.compile(r"\]$")

class OpenBrace(OpenDelimiter):
    recognizer = re.compile(r"\{$")

class CloseBrace(CloseDelimiter):
    recognizer = re.compile(r"\}$")

class Pipe(SequentialDelimiter, OpenDelimiter, CloseDelimiter):
    recognizer = re.compile(r"\|$")

class StringLiteral(Token):
    prefix_recognizer = re.compile(r'"[^"]*$')
    recognizer = re.compile(r'".*"$')

class InternLiteral(Token):
    prefix_recognizer = re.compile(r"'[^']*$")
    recognizer = re.compile(r"'.*'$")

class IntegerLiteral(Token):
    recognizer = re.compile(r"\d+$")

class BooleanLiteral(Reserved):
    recognizer = re.compile(r"(?:Truth)$|(?:Falsity)$")

class VoidLiteral(Reserved):
    recognizer = re.compile(r"Void$")


class Commentary(Token):
    def __init__(self, *_):
        # it's not meant for us; don't even bother reading it
        self.representation = ''

    prefix_recognizer = re.compile(r"#.*$")
    recognizer = re.compile(r"#.*\n$")

class EndOfFile(Token):
    recognizer = re.compile(r"█$")


class TokenizingException(ValueError):
    ...

class BaseLexer:
    def __init__(self, tokenclasses):
        self.tokenclasses = tokenclasses
        self.tokens = []

    def skip_whitespace(self):
        while self.source[self.candidate_start] in ' \n\t':
            self.candidate_start += 1  # skip whitespace

    def chomp_and_resynchronize(self):
        matched = self.sight[0]
        # contemptibly, '$' can also match "just before the newline at
        # the end of the string"
        matched.representation = matched.representation.rstrip('\n')
        self.tokens.append(matched)
        self.sight = []
        self.candidate_start = self.candidate_end - 1
        self.skip_whitespace()
        self.candidate_end = self.candidate_start + 1

    @staticmethod
    def _handle_tokenizing_error(sight, candidate):
        if len(sight) == 0:
            raise TokenizingException(
                "Couldn't tokenize {}".format(candidate)
            )
        else:
            raise TokenizingException(
                "Ambiguous input: {} are tied as the longest "
                "tokenizations of {}".format(
                    ', '.join(map(str, sight)), candidate)
            )

    def tokenize(self, source):
        self.source = source + '█'  # end-of-file sentinel
        self.candidate_start = 0
        self.candidate_end = 1
        self.skip_whitespace()
        self.sight = []
        while self.candidate_end <= len(self.source):
            candidate = self.source[self.candidate_start:self.candidate_end]
            logger.debug("Entering tokenization loop for '%s' "
                         "with candidate indices %s:%s",
                         candidate, self.candidate_start, self.candidate_end)
            premonition = list(filter(
                lambda x: x,
                [tokenclass.match(candidate)
                 for tokenclass in self.tokenclasses]
            ))
            logger.debug("Premonition: %s", premonition)
            if premonition:
                self.sight = premonition
                self.candidate_end += 1
            else:
                # With an empty premonition, we lose all hope for
                # partially-matched subtokens.
                self.sight = [visible for visible in self.sight
                              if isinstance(visible, Token)]
                if len(self.sight) == 1 and isinstance(self.sight[0], Token):
                    # Match!
                    self.chomp_and_resynchronize()
                elif any(isinstance(t, Reserved) for t in self.sight):
                    # Multimatch but one is one of the langague's
                    # reserved words and takes priority!
                    self.sight = [t for t in self.sight
                                  if isinstance(t, Reserved)]
                    self.chomp_and_resynchronize()
                else:
                    # No match or erroneous multimatch!
                    self._handle_tokenizing_error(self.sight, candidate)
        return self.tokens

BASE_KEYWORDS = [If, For, Lambda, Def, SubscriptDef, Deflambda]
TYPE_SPECIFIERS = [IntegerSpecifer, StringSpecifier, Arrow]
TOKENCLASSES = BASE_KEYWORDS + TYPE_SPECIFIERS + [
    Identifier,
    OpenParenthesis, CloseParenthesis,
    OpenBracket, CloseBracket,
    OpenBrace, CloseBrace,
    Pipe,
    StringLiteral, InternLiteral,
    IntegerLiteral,
    BooleanLiteral, VoidLiteral,
    Commentary,
    EndOfFile
]

class Lexer(BaseLexer):
    def __init__(self):
        super().__init__(TOKENCLASSES)


def lex(source):
    return LookaheadStream(Lexer().tokenize(source))
