from lexer import *  # yeah, yeah
from utils import push

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class Expression:
    ...

class Codeform(Expression):
    ...

class Definition(Codeform):
    def __init__(self, identifier, identified):
        self.identifier = identifier
        self.identified = identified

    def __repr__(self):
        return "<{}: {}:={}>".format(
            self.__class__.__name__,
            self.identifier, self.identified
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

class Application(Codeform):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return "<{}: ({}, {})>".format(
            self.__class__.__name__,
            self.function.value, ' '.join(repr(arg) for arg in self.arguments)
        )

class Atom(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

class IntegerAtom(Atom):
    ...

class StringAtom(Atom):
    ...

class IdentifierAtom(Atom):
    ...

class PrimitiveAtom(Atom):
    ...

class ParsingException(Exception):
    ...

def parse_codeform(tokenstream):
    open_paren = next(tokenstream)
    if not isinstance(open_paren, OpenParenthesis):
        raise ParsingException(
            "Expected an open parenthesis token, got {}.".format(open_paren))
    first = parse_expression(tokenstream)
    rest = []
    done_here = False
    while not done_here:
        next_token = next(tokenstream)
        if isinstance(next_token, CloseParenthesis):
            done_here = True
        else:
            rest.append(parse_expression(push(tokenstream, next_token)))

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
                raise ParsingException("Definition must have 2 arguments.")
            if not isinstance(rest[0], IdentifierAtom):
                raise ParsingException("First argument to definition must be "
                                       "identifier.")
            return Definition(*rest)


def parse_expression(tokenstream):
    leading_token = next(tokenstream)
    while isinstance(leading_token, Commentary):
        leading_token = next(tokenstream)

    if isinstance(leading_token, OpenParenthesis):
        return parse_codeform(push(tokenstream, leading_token))
    else:
        expression_token = leading_token
        if isinstance(expression_token, Keyword):
            return PrimitiveAtom(expression_token.representation)
        elif isinstance(expression_token, IntegerLiteral):
            return IntegerAtom(int(leading_token.representation))
        elif isinstance(expression_token, StringLiteral):
            return StringAtom(expression_token.representation.strip('"'))
        elif isinstance(expression_token, Identifier):
            return IdentifierAtom(expression_token.representation)

def parse(tokenstream):
    expressions = []
    while True:  # XXX this is awful
        try:
            expressions.append(parse_expression(tokenstream))
        except StopIteration:
            break
    return expressions
