import logging
import os
import re

IDENTIFIER = re.compile(r"[-A-Za-z:λ_]+$")

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

class Token:
    def __init__(self, representation):
        self.representation = representation

    @classmethod
    def match(cls, source_fragment):
        if cls.recognizer.match(source_fragment):
            return cls(source_fragment)
        elif getattr(cls, 'prefix_recognizer',
                     re.compile('$^')).match(source_fragment):
            return True  # not a valid match, but the prefix of one
        else:
            return None

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.representation == other.representation)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__,
                                 self.representation)


class Keyword(Token):
    ...

class If(Keyword):
    recognizer = re.compile(r"if$")

class Lambda(Keyword):
    recognizer = re.compile(r"λ$")

class Def(Keyword):
    recognizer = re.compile(r":=$")

class Deflambda(Keyword):
    recognizer = re.compile(r"λ:=$")


class Identifier(Token):
    recognizer = IDENTIFIER


class TypeSpecifier(Keyword):
    ...

class IntegerSpecifer(TypeSpecifier):
    recognizer = re.compile(r":int$")

class StringSpecifier(TypeSpecifier):
    recognizer = re.compile(r":str$")


class OpenDelimiter(Token):
    ...

class CloseDelimiter(Token):
    ...

class OpenParenthesis(OpenDelimiter):
    recognizer = re.compile(r"\($")

class CloseParenthesis(CloseDelimiter):
    recognizer = re.compile(r"\)$")

class OpenBracket(OpenDelimiter):
    recognizer = re.compile(r"\[$")

class CloseBracket(CloseDelimiter):
    recognizer = re.compile(r"\]$")

class OpenBrace(OpenDelimiter):
    recognizer = re.compile(r"\{$")

class CloseBrace(CloseDelimiter):
    recognizer = re.compile(r"\}$")


class StringLiteral(Token):
    prefix_recognizer = re.compile(r'"[^"]*$')
    recognizer = re.compile(r'".*"$')

class InternLiteral(Token):
    prefix_recognizer = re.compile(r"'[^']*$")
    recognizer = re.compile(r"'.*'$")


class IntegerLiteral(Token):
    recognizer = re.compile(r"\d+$")

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

    def chomp_and_resynchronize(self):
        self.tokens.append(self.sight[0])
        self.candidate_start = self.candidate_end - 1
        while self.source[self.candidate_start] in ' \n\t':
            self.candidate_start += 1  # skip whitespace
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
                if len(self.sight) == 1 and isinstance(self.sight[0], Token):
                    self.chomp_and_resynchronize()
                elif any(isinstance(t, Keyword) for t in self.sight):
                    self.sight = [t for t in self.sight
                                  if isinstance(t, Keyword)]
                    self.chomp_and_resynchronize()
                else:
                    self._handle_tokenizing_error(self.sight, candidate)
        return self.tokens

BASE_KEYWORDS = [If, Lambda, Def, Deflambda]
TYPE_SPECIFIERS = [IntegerSpecifer, StringSpecifier]
TOKENCLASSES = BASE_KEYWORDS + TYPE_SPECIFIERS + [
    Identifier,
    OpenParenthesis, CloseParenthesis,
    OpenBracket, CloseBracket,
    OpenBrace, CloseBrace,
    StringLiteral, InternLiteral,
    IntegerLiteral,
    Commentary,
    EndOfFile
]

class Lexer(BaseLexer):
    def __init__(self):
        super().__init__(TOKENCLASSES)


def lex(source):
    return iter(Lexer().tokenize(source))
