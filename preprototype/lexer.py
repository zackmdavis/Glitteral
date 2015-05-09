import logging
import os
import re

IDENTIFIER = re.compile(r"[-A-Za-z_]+$")

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

class Token:
    def __init__(self, value):
        self.value = value

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
        return self.value == other.value

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.value)

class Identifier(Token):
    recognizer = IDENTIFIER

class OpenDelimiter(Token):
    ...

class CloseDelimiter(Token):
    ...

class OpenParenthesis(OpenDelimiter):
    recognizer = re.compile(r"\($")

class CloseParenthesis(CloseDelimiter):
    recognizer = re.compile(r"\)$")

class StringLiteral(Token):
    prefix_recognizer = re.compile(r'"[^"]*$')
    recognizer = re.compile(r'".*"$')

class InternLiteral(Token):
    prefix_recognizer = re.compile(r"'[^']*$")
    recognizer = re.compile(r"'.*'$")

class IntegerLiteral(Token):
    recognizer = re.compile(r"\d+$")

class EndOfFile(Token):
    recognizer = re.compile(r"█$")

class TokenizingException(ValueError):
    ...

class BaseTokenizer:
    def __init__(self, tokenclasses):
        self.tokenclasses = tokenclasses
        self.tokens = []

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
                    ', '.join(sight), candidate)
            )

    def tokenize(self, source):
        source += '█'  # end-of-file sentinel
        candidate_start = 0
        candidate_end = 1
        sight = []
        while candidate_end <= len(source):
            candidate = source[candidate_start:candidate_end]
            logger.debug("Entering tokenization loop for '%s' "
                         "with candidate indices %s:%s",
                         candidate, candidate_start, candidate_end)
            premonition = list(filter(
                lambda x: x,
                [tokenclass.match(candidate)
                 for tokenclass in self.tokenclasses]
            ))
            logger.debug("Premonition: %s", premonition)
            if premonition:
                sight = premonition
                candidate_end += 1
            else:
                if len(sight) == 1 and isinstance(sight[0], Token):
                    self.tokens.append(sight[0])
                    candidate_start = candidate_end - 1
                    while source[candidate_start] in ' \n\t':
                        candidate_start += 1  # skip whitespace
                    candidate_end = candidate_start + 1
                else:
                    self._handle_tokenizing_error(sight, candidate)
        return self.tokens

TOKENCLASSES = [Identifier, OpenParenthesis, CloseParenthesis,
                StringLiteral, InternLiteral, IntegerLiteral, EndOfFile]

class Tokenizer(BaseTokenizer):
    def __init__(self):
        super().__init__(TOKENCLASSES)
