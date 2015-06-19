import logging
import os
import re

from collections import namedtuple

from utils import LookaheadStream, get_logger


logger = get_logger(__name__)

INDENTATION_WIDTH = 3

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
        return "<{}{}>".format(
            self.__class__.__name__,
            (": {}".format(repr(self.representation))
             if self.representation is not None else '')
        )


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

class Arrow(Reserved):
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
FloatSpecifer = type_specifier_class("Float", "float")
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


class Ellipsis(Reserved):
    recognizer = re.compile("…$(?!\n)")

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
    prefix_recognizer = re.compile(r'"[^"]*$(?!\n)')
    recognizer = re.compile(r'".*"$(?!\n)')

class InternLiteral(Token):
    prefix_recognizer = re.compile(r"'[^']*$(?!\n)")
    recognizer = re.compile(r"'.*'$(?!\n)")

class IntegerLiteral(Token):
    recognizer = re.compile(r"\d+$(?!\n)")

class FloatLiteral(Token):
    prefix_recognizer = re.compile("[0-9.]$(?!\n)")
    recognizer = re.compile(r"(\d+\.\d*$(?!\n))|(\.\d+$(?!\n))")

class BooleanLiteral(Reserved):
    recognizer = re.compile(r"(Truth$(?!\n))|(Falsity$(?!\n))")

class VoidLiteral(Reserved):
    recognizer = re.compile(r"Void$(?!\n)")


# Some might argue that our current handling of indentation tokens is
# slightly recondite (we _hope_ they would not say _sloppy_!): token
# recognition mostly happens as usual with our `prefix_recognizer` and
# `recognizer` regexes, with the detail that the recognizer is
# determined dynamically from the current indentation level. But the
# token that gets recognized isn't the same as the token or tokens
# that ultimately get emitted; we analyze the representation of the
# recognized token and decide how many tokens to actually emit during
# the chomp-and-resynchronization phase.

class AbstractDent(Token):
    prefix_recognizer = re.compile(r"\n *$(?!\n)", re.MULTILINE)

    def __init__(self, *args):
        if not args:
            self.representation = None
        else:
            super().__init__(*args)

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
            return re.compile(r"\n(   ){%d,}$(?!\n)" %
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
                return re.compile(r"\n(   ){,%d}$(?!\n)" %
                                  (lexer_context.indentation_level - 1),
                                  re.MULTILINE)
            else:
                # we cannot dedent past the left margin
                return re.compile(r"(?!)")
        else:
            # we don't care
            return re.compile(r"(?!)")

class AlignedNewline(AbstractDent):
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

    recognizer = re.compile(r"#.*$(?!\n)")


class EndOfFile(Token):
    recognizer = re.compile(r"█$(?!\n)")


class TokenizingException(ValueError):
    ...

class IndentationException(TokenizingException):
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

    def skip_insignificant_whitespace(self):
        if self.undelimited():
            # If we're not being delimited, skip spaces (so we can try
            # to match the newline-and-leading-spaces-of-next-line)
            self.skip_spaces()
        else:
            # If we are being delimited, we don't care about
            # whitespace in any form
            self.skip_whitespace()

    def indentation_match_special_handling(self, matched):
        new_offset = int(len(matched.representation.strip('\n')) /
                         INDENTATION_WIDTH)
        if new_offset != self.indentation_level:
            if new_offset > self.indentation_level:
                dent_class = Indent
            elif new_offset < self.indentation_level:
                dent_class = Dedent
            for _ in range(abs(new_offset - self.indentation_level)):
                self.tokens.append(dent_class())
                self.indentation_level += matched.delta_indentation

    def delimiter_match_special_handling(self, matched):
        # We do this very limited amount of parsing here in the lexer module so
        # that we can know what indent and dedent tokens to emit.
        self.delimiter_stack.append(matched)
        if len(self.delimiter_stack) >= 2:
            penultimate, last = self.delimiter_stack[-2:]
            if isinstance(last, penultimate.opposite):
                for _ in range(2):
                    self.delimiter_stack.pop()

    def chomp_and_resynchronize(self):
        matched = self.sight[0]

        if isinstance(matched, AbstractDent):
            self.indentation_match_special_handling(matched)
        else:
            if not isinstance(matched, Commentary):
                self.tokens.append(matched)

        if isinstance(matched, Delimiter):
            self.delimiter_match_special_handling(matched)

        self.sight = []
        self.candidate_start = self.candidate_end - 1
        self.skip_insignificant_whitespace()
        self.candidate_end = self.candidate_start + 1

    @staticmethod
    def _handle_tokenizing_error(sight, candidate):
        if len(sight) == 0:
            if candidate.startswith("\n "):
                raise IndentationException(
                    "Indentation levels must be exactly {} spaces.".format(
                        INDENTATION_WIDTH))
            raise TokenizingException(
                "Couldn't tokenize {}".format(candidate))
        else:
            raise TokenizingException(
                "Ambiguous input: {} are tied as the longest "
                "tokenizations of {}".format(
                    ', '.join(map(str, sight)), candidate))

    def tokenize(self, source):
        self.source = source + '█'  # end-of-file sentinel
        self.candidate_start = 0
        self.candidate_end = 1
        self.tokens = []
        self.skip_insignificant_whitespace()
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
    IntegerSpecifer, FloatSpecifer, StringSpecifier, BooleanSpecifier,
    IntegerListSpecifier, StringListSpecifier,
    Arrow
]
OTHER_RESERVED = [Dash, Ellipsis]
INDENTATION = [Indent, Dedent, AlignedNewline]
TOKENCLASSES = BASE_KEYWORDS + TYPE_SPECIFIERS + OTHER_RESERVED + INDENTATION + [
    Identifier,
    OpenParenthesis, CloseParenthesis,
    OpenBracket, CloseBracket,
    OpenBrace, CloseBrace,
    Semicolon,
    Pipe,
    IntegerLiteral, FloatLiteral,
    StringLiteral, InternLiteral,
    BooleanLiteral, VoidLiteral,
    Commentary,
    EndOfFile
]

class Lexer(BaseLexer):
    def __init__(self):
        super().__init__(TOKENCLASSES)


def lex(source):
    return LookaheadStream(Lexer().tokenize(source))
