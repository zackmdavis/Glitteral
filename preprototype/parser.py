from lexer import *  # yeah, yeah
from utils import push

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class Expression:
    ...

class Codeform(Expression):
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest

    def __repr__(self):
        return "<{}: ({}, {})>".format(self.__class__.__name__,
                                       self.first, self.rest)

class Atom(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__,
                                 self.value)

class IntegerAtom(Atom):
    ...

class StringAtom(Atom):
    ...

class IdentifierAtom(Atom):
    ...

class BuiltinAtom(Atom):
    ...

class ParsingException(Exception):
    ...

def parse_codeform(tokenstream):
    open_paren = next(tokenstream)
    if not isinstance(open_paren, OpenParenthesis):
        raise ParsingException(
            "Expected an open parenthesis token, got {}".format(open_paren))
    first = parse_expression(tokenstream)
    rest = []
    done_here = False
    while not done_here:
        next_token = next(tokenstream)
        if isinstance(next_token, CloseParenthesis):
            done_here = True
        else:
            rest.append(parse_expression(push(tokenstream, next_token)))
    return Codeform(first, rest)

def parse_expression(tokenstream):
    try:
        leading_token = next(tokenstream)
    except StopIteration:
        return None

    if isinstance(leading_token, OpenParenthesis):
        return parse_codeform(push(tokenstream, leading_token))
    else:
        expression_token = leading_token
        if isinstance(expression_token, Keyword):
            return BuiltinAtom(expression_token.representation)
        elif isinstance(expression_token, IntegerLiteral):
            return IntegerAtom(int(leading_token.representation))
        elif isinstance(expression_token, StringLiteral):
            return StringAtom(expression_token.representation.strip('"'))
        elif isinstance(expression_token, Identifier):
            return IdentifierAtom(expression_token.representation)
