from collections import namedtuple

from lexer import *  # yeah, yeah
from utils import twopartitions

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class Expression:
    mutable = False  # unless otherwise overridden

class Codeform(Expression):
    ...

Argument = namedtuple('Argument', ('name', 'type'))

class NamedFunctionDefinition(Codeform):
    def __init__(self, name, argument_sequential, return_type, expressions):
        self.name = name
        self.arguments = [Argument(name, type_specifier)
                          for name, type_specifier
                          in twopartitions(argument_sequential.elements)]
        self.return_type = return_type
        self.expressions = expressions

    def __repr__(self):
        return "<{}: {}({}) → {}>".format(
            self.__class__.__name__,
            self.name, self.arguments,
            self.return_type
        )

class Definition(Codeform):
    def __init__(self, identifier, identified):
        self.identifier = identifier
        self.identified = identified

    def __repr__(self):
        return "<{}: {}:={}>".format(
            self.__class__.__name__,
            self.identifier, self.identified
        )

class SubscriptAssignment(Codeform):
    def __init__(self, collection_identifier, key, value):
        self.collection_identifier = collection_identifier
        self.key = key
        self.value = value

    def __repr__(self):
        return "<{}: {}_{}:={}>".format(
            self.__class__.__name__,
            self.collection_identifier, self.key, self.value
        )

class Conditional(Codeform):
    def __init__(self, condition, consequent, alternative=None):
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    def __repr__(self):
        return "<{}: ({}, {}/{})>".format(
            self.__class__.__name__,
            self.condition, self.consequent, self.alternative
        )

class DeterminateIteration(Codeform):
    def __init__(self, index_identifier, iterable, body):
        self.index_identifier = index_identifier
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return "<{}: [{} {}]>".format(
            self.__class__.__name__,
            self.index_identifier, self.iterable
        )

class Application(Codeform):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return "<{}: ({}, {})>".format(
            self.__class__.__name__,
            self.function.value, ' '.join(repr(arg) for arg in self.arguments)
        )


class Sequential(Expression):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return "<{}: {}{}{}>".format(
            self.__class__.__name__,
            self.open_delimiter, ' '.join(repr(el) for el in self.elements),
            self.close_delimiter
        )

class List(Sequential):
    mutable = True
    open_delimiter = '['
    close_delimiter = ']'

class Vector(Sequential):
    open_delimiter = close_delimiter = '|'


class Atom(Expression):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.value == other.value)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.value)

class IntegerAtom(Atom):
    ...

class StringAtom(Atom):
    ...

class BooleanAtom(Atom):
    ...

class VoidAtom(Atom):
    ...

class IdentifierAtom(Atom):
    ...

class PrimitiveAtom(Atom):
    ...

class TypeSpecifierAtom(PrimitiveAtom):
    ...

class BuiltinAtom(Atom):
    # maybe distinguish builtin functions from ordinary identifiers?
    ...

class ParsingException(Exception):
    ...

def parse_codeform(tokenstream):
    open_paren = tokenstream.pop()
    if not isinstance(open_paren, OpenParenthesis):
        raise ParsingException(
            "Expected an open parenthesis token, got {}.".format(open_paren))
    first = parse_expression(tokenstream)
    rest = []
    done_here = False
    while not done_here:
        next_token = tokenstream.peek()
        if isinstance(next_token, CloseParenthesis):
            tokenstream.pop()
            done_here = True
        else:
            rest.append(parse_expression(tokenstream))

    if isinstance(first, IdentifierAtom):
        return Application(first, rest)
    elif isinstance(first, PrimitiveAtom):
        if first.value == "if":
            if len(rest) not in (2, 3):
                raise ParsingException("Conditional expression must have 2 or "
                                       "3 arguments.")
            return Conditional(*rest)
        elif first.value == ":=":
            if len(rest) != 2:
                raise ParsingException("Definition must have 2 arguments, got "
                                       "%s", rest)
            if not isinstance(rest[0], IdentifierAtom):
                raise ParsingException("First argument to definition must be "
                                       "identifier.")
            return Definition(*rest)
        elif first.value == "_:=":
            if len(rest) != 3:
                raise ParsingException("Subscript assignment must have 3 "
                                       "arguments, got {}".format(rest))
            return SubscriptAssignment(*rest)
        elif first.value == ":=λ":
            # TODO: error checking
            name, argument_sequential, _arrow, return_type, *expressions = rest
            return NamedFunctionDefinition(
                name, argument_sequential, return_type, expressions)
        elif first.value == "for":
            bindings, *body = rest
            index_identifier, iterable = bindings.elements
            return DeterminateIteration(index_identifier, iterable, body)

def parse_sequential(tokenstream):
    open_delimiter = tokenstream.pop()
    if not (isinstance(open_delimiter, SequentialDelimiter) or
            not isinstance(open_delimiter, OpenDelimiter)):
        raise ParsingException("Expected an opening sequential delimiter ('[' "
                               "or '|'), got {}".format(open_delimiter))
    if isinstance(open_delimiter, OpenBracket):
        sequential_class = List
    elif isinstance(open_delimiter, Pipe):
        sequential_class = Vector
    elements = []
    done_here = False
    # TODO: unify this loop with its analogue in parse_codeform?
    while not done_here:
        next_token = tokenstream.peek()
        if (isinstance(next_token, SequentialDelimiter) and
            isinstance(next_token, CloseDelimiter)):
            tokenstream.pop()
            done_here = True
        else:
            elements.append(parse_expression(tokenstream))
    return sequential_class(elements)


def parse_expression(tokenstream):
    leading_token = tokenstream.peek()
    logger.debug("leading_token in parse_expression is %s", leading_token)
    while isinstance(leading_token, Commentary):
        tokenstream.pop()
        leading_token = tokenstream.peek()

    if isinstance(leading_token, OpenDelimiter):  # collections
        if isinstance(leading_token, OpenParenthesis):
            return parse_codeform(tokenstream)
        elif (isinstance(leading_token, OpenBracket) or
            isinstance(leading_token, Pipe)):
            return parse_sequential(tokenstream)
    else:  # atoms
        expression_token = tokenstream.pop()
        if isinstance(expression_token, Keyword):
            return PrimitiveAtom(expression_token.representation)
        if isinstance(expression_token, TypeSpecifier):
            return TypeSpecifierAtom(expression_token.representation)
        elif isinstance(expression_token, IntegerLiteral):
            return IntegerAtom(int(leading_token.representation))
        elif isinstance(expression_token, StringLiteral):
            return StringAtom(expression_token.representation.strip('"'))
        elif isinstance(expression_token, BooleanLiteral):
            return (BooleanAtom(True)
                    if expression_token.representation == "Truth"
                    else BooleanAtom(False))
        elif isinstance(expression_token, VoidLiteral):
            return VoidLiteral(None)
        elif isinstance(expression_token, Identifier):
            return IdentifierAtom(expression_token.representation)
        else:
            raise ParsingException("Failed to recognize an expression from "
                                   "{}".format(expression_token))

def parse(tokenstream):
    while True:
        yield parse_expression(tokenstream)
