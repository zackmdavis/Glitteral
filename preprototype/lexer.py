import logging
import os
import re

from collections import namedtuple

from utils import LookaheadStream, get_logger

logger = get_logger(__name__)

PartiallyMatchedSubtoken = namedtuple('PartiallyMatchedSubtoken',
                                      ('tokenclass', 'representation'))

class Token:
    def __init__(self, representation):
        self.representation = representation

    @classmethod
    def match(cls, source_fragment, **kwargs):
        if cls.recognizer.match(source_fragment):
            return cls(source_fragment)
        elif getattr(cls, 'prefix_recognizer',
                     # the empty string is a prefix of anything
                     re.compile('^(?![\s\S])')).match(source_fragment):
            return PartiallyMatchedSubtoken(
                cls.__name__, source_fragment)
        else:
            return None

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.representation == other.representation)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__,
                                 repr(self.representation))


# word characters, plus hyphen, plus ?! for predicates and living
# dangerously, plus :=≠+−⋅÷&∨∀∃ to support our assignment, math, and
# logical operations
IDENTIFIER_CHARS = r"\w\-:=≠+−⋅÷!?&∨∀∃"

class Reserved(Token):
    ...

class Keyword(Reserved):
    ...

class If(Keyword):
    recognizer = re.compile(r"if$(?!\n)")

class When(Keyword):
    recognizer = re.compile(r"when$(?!\n)")

class For(Keyword):
    recognizer = re.compile(r"for$(?!\n)")

class While(Keyword):
    recognizer = re.compile(r"while$(?!\n)")

class Do(Keyword):
    recognizer = re.compile(r"do$(?!\n)")

class Lambda(Keyword):
    recognizer = re.compile(r"λ$(?!\n)")

class Def(Keyword):
    recognizer = re.compile(r":=$(?!\n)")

class Deflambda(Keyword):
    recognizer = re.compile(r":=λ$(?!\n)")

class SubscriptDef(Keyword):
    recognizer = re.compile(r"_:=$(?!\n)")


class Dash(Reserved):
    recognizer = re.compile(r"—$(?!\n)")

class Arrow(Keyword):
    recognizer = re.compile(r"→$(?!\n)")

class Identifier(Token):
    # simplify regex-based distinguishing of numeric literals from
    # identifiers by preventing the latter from starting with a digit,
    # as simulated by a negative lookahead assertion
    recognizer = re.compile("(?![0-9])[{0}][{0}]*$(?!\n)".format(
        IDENTIFIER_CHARS))

class TypeSpecifier(Reserved):
    prefix_recognizer = re.compile(r"\^\w*$(?!\n)")

def type_specifier_class(type_name, type_specifier):
    return type(
        "{}Specifier".format(type_name),
        (TypeSpecifier,),
        {'recognizer': re.compile(r"\^{}$(?!\n)".format(type_specifier))}
    )

IntegerSpecifer = type_specifier_class("Integer", "int")
StringSpecifier = type_specifier_class("String", "str")
BooleanSpecifier = type_specifier_class("Boolean", "bool")

# XXX UNCIVILIZED: composing the regexes to do this in a DRYer (Don't
# Repeat Yourself) way is an intricate task, so I'm OK with leaving
# this area DAMP (Duplicated Areas of My Program) for now while I
# advance the project along other fronts
class IntegerListSpecifier(TypeSpecifier):
    prefix_recognizer = re.compile(r"(\^\[$)|(\^\[i$)|(\^\[in$)|(\^\[int$)")
    recognizer = re.compile(r"\^\[int]$(?!\n)")

class StringListSpecifier(TypeSpecifier):
    prefix_recognizer = re.compile(r"(\^\[$)|(\^\[s$)|(\^\[st$)|(\^\[str$)")
    recognizer = re.compile(r"\^\[str]$(?!\n)")


class Delimiter(Token):
    ...

class OpenDelimiter(Delimiter):
    ...

class CloseDelimiter(Delimiter):
    ...

class SequentialDelimiter(Token):
    ...

class AssociativeDelimiter(Token):
    ...

class OpenParenthesis(OpenDelimiter):
    recognizer = re.compile(r"\($(?!\n)")

    @property
    def opposite(self):
        return CloseParenthesis

class CloseParenthesis(CloseDelimiter):
    recognizer = re.compile(r"\)$(?!\n)")

    @property
    def opposite(self):
        return OpenParenthesis

class OpenBracket(SequentialDelimiter, OpenDelimiter):
    recognizer = re.compile(r"\[$(?!\n)")

    @property
    def opposite(self):
        return CloseBracket

class CloseBracket(SequentialDelimiter, CloseDelimiter):
    recognizer = re.compile(r"\]$(?!\n)")

    @property
    def opposite(self):
        return OpenBracket

class OpenBrace(AssociativeDelimiter, OpenDelimiter):
    recognizer = re.compile(r"\{$(?!\n)")

    @property
    def opposite(self):
        return CloseBrace

class CloseBrace(AssociativeDelimiter, CloseDelimiter):
    recognizer = re.compile(r"\}$(?!\n)")

    @property
    def opposite(self):
        return OpenBrace

class Semicolon(Token):
    recognizer = re.compile(";$(?!\n)")

class Pipe(SequentialDelimiter, OpenDelimiter, CloseDelimiter):
    recognizer = re.compile(r"\|$(?!\n)")

    @property
    def opposite(self):
        return Pipe

class StringLiteral(Token):
    prefix_recognizer = re.compile(r'"[^"]*$')
    recognizer = re.compile(r'".*"$')

class InternLiteral(Token):
    prefix_recognizer = re.compile(r"'[^']*$(?!\n)")
    recognizer = re.compile(r"'.*'$(?!\n)")

class IntegerLiteral(Token):
    recognizer = re.compile(r"\d+$(?!\n)")

class BooleanLiteral(Reserved):
    recognizer = re.compile(r"(?:Truth)$|(?:Falsity)$(?!\n)")

class VoidLiteral(Reserved):
    recognizer = re.compile(r"Void$(?!\n)")


class AbstractDent(Token):
    prefix_recognizer = re.compile(r"\n *$(?!\n)", re.MULTILINE)

    @classmethod
    def match(cls, source_fragment, *, lexer_context):
        # CAUTION: monkey-patching a class variable (trust me on this one)
        cls.recognizer = cls.recognizer_from_lexer_context(lexer_context)
        return super().match(source_fragment)

class Indent(AbstractDent):
    delta_indentation = 1

    @classmethod
    def recognizer_from_lexer_context(self, lexer_context):
        if lexer_context.undelimited():
            return re.compile(r"\n(?:   ){%d}$(?!\n)" %
                               (lexer_context.indentation_level + 1),
                               re.MULTILINE)
        else:
            # we don't care about indentation between delimiters
            return re.compile(r"(?!)")

class Dedent(AbstractDent):
    delta_indentation = -1

    @classmethod
    def recognizer_from_lexer_context(self, lexer_context):
        if lexer_context.undelimited():
            if lexer_context.indentation_level:
                return re.compile(r"\n(?:   ){%d}$(?!\n)" %
                                  (lexer_context.indentation_level - 1),
                                  re.MULTILINE)
            else:
                # we cannot dedent past the left margin
                return re.compile(r"(?!)")
        else:
            # we don't care
            return re.compile(r"(?!)")

class ConstantIndentation(AbstractDent):
    delta_indentation = 0

    @classmethod
    def recognizer_from_lexer_context(self, lexer_context):
        if lexer_context.undelimited():
            return re.compile(r"\n(?:   ){%d}(?!\n)$" %
                              lexer_context.indentation_level,
                              re.MULTILINE)
        else:
            # we don't care about indentation between delimiters
            return re.compile(r"(?!)")


class Commentary(Token):
    def __init__(self, *_):
        # it's not meant for us; don't even bother reading it
        self.representation = ''

    prefix_recognizer = re.compile(r"#.*$(?!\n)")
    recognizer = re.compile(r"#.*\n$(?!\n)")


class EndOfFile(Token):
    recognizer = re.compile(r"█$(?!\n)")


class TokenizingException(ValueError):
    ...

class PreparsingException(Exception):
    # TODO? raise this if we can detect an error during the preparsing of
    # delimiters that we do for significant whitespace purposes
    ...

class BaseLexer:
    def __init__(self, tokenclasses):
        self.tokenclasses = tokenclasses
        self.tokens = []

        self.delimiter_stack = []
        self.sight = []
        self.indentation_level = 0

    def skip_character_class(self, character_class):
        while self.source[self.candidate_start] in character_class:
            self.candidate_start += 1

    def skip_spaces(self):
        self.skip_character_class(' ')

    def skip_whitespace(self):
        self.skip_character_class(' \n\t')

    def undelimited(self):
        return not self.delimiter_stack

    def chomp_and_resynchronize(self):
        matched = self.sight[0]
        self.tokens.append(matched)

        if isinstance(matched, AbstractDent):
            self.indentation_level += matched.delta_indentation

        # We do this very limited amount of parsing here in the lexer module so
        # that we can know what indent and dedent tokens to emit.
        if isinstance(matched, Delimiter):
            self.delimiter_stack.append(matched)
            if len(self.delimiter_stack) >= 2:
                penultimate, last = self.delimiter_stack[-2:]
                if isinstance(last, penultimate.opposite):
                    for _ in range(2):
                        self.delimiter_stack.pop()

        self.sight = []
        self.candidate_start = self.candidate_end - 1
        if self.undelimited():
            # If we're not being delimited, skip spaces (so we can try
            # to match the newline-and-leading-spaces-of-next-line)
            self.skip_spaces()
        else:
            # If we are being delimited, we don't care about
            # whitespace in any form
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
        self.tokens = []
        if self.undelimited():
            self.skip_spaces()
        else:
            self.skip_whitespace()
        while self.candidate_end <= len(self.source):
            candidate = self.source[self.candidate_start:self.candidate_end]
            logger.debug("Entering tokenization loop for %r "
                         "with candidate indices %s:%s",
                         candidate, self.candidate_start, self.candidate_end)
            premonition = list(filter(
                lambda x: x,
                [tokenclass.match(candidate, lexer_context=self)
                 for tokenclass in self.tokenclasses]
            ))
            logger.debug("Sight: %s", self.sight)
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

BASE_KEYWORDS = [If, When, For, While, Lambda, Def, SubscriptDef, Deflambda, Do]
TYPE_SPECIFIERS = [
    IntegerSpecifer, StringSpecifier, BooleanSpecifier,
    IntegerListSpecifier, StringListSpecifier,
    Arrow
]
OTHER_RESERVED = [Dash]
INDENTATION = [Indent, Dedent, ConstantIndentation]
TOKENCLASSES = BASE_KEYWORDS + TYPE_SPECIFIERS + OTHER_RESERVED + INDENTATION + [
    Identifier,
    OpenParenthesis, CloseParenthesis,
    OpenBracket, CloseBracket,
    OpenBrace, CloseBrace,
    Semicolon,
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
