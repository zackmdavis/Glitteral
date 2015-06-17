from collections import namedtuple, ChainMap

from lexer import *  # yeah, yeah
from utils import twopartitions, get_logger, oxford_series

logger = get_logger(__name__)


class Expression:
    # unless otherwise overridden
    mutable = False

    def __init__(self):
        # These will be reassigned during annotation.
        self.global_environment = {}
        self.local_environment = {}
        self.statementlike = None

    @property
    def environment(self):
        return ChainMap(self.local_environment, self.global_environment)

class Codeform(Expression):
    def __init__(self):
        super().__init__()


class NamedFunctionDefinition(Codeform):
    def __init__(self, name, argument_sequential, return_type, expressions):
        super().__init__()
        self.name = name
        self.arguments = [Argument(name, type_specifier)
                          for name, type_specifier
                          in twopartitions(argument_sequential.elements)]
        self.return_type = return_type
        self.expressions = expressions

    @property
    def children(self):
        return self.expressions

    def __repr__(self):
        return "<{}: {}({}) → {}>".format(
            self.__class__.__name__,
            self.name, self.arguments,
            self.return_type
        )

class Definition(Codeform):
    def __init__(self, identifier, identified):
        super().__init__()
        self.identifier = identifier
        self.identified = identified

        # XXX??
        self.identifier.statementlike = False

    @property
    def children(self):
        return [self.identifier, self.identified]

    def __repr__(self):
        return "<{}: {}:={}>".format(
            self.__class__.__name__,
            self.identifier, self.identified
        )


class DoBlock(Codeform):
    def __init__(self, expressions):
        super().__init__()
        self.expressions = expressions

    @property
    def children(self):
        return self.expressions

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.expressions)


class SubscriptAssignment(Codeform):
    def __init__(self, collection_identifier, key, value):
        super().__init__()
        self.collection_identifier = collection_identifier
        self.key = key
        self.value = value

    @property
    def children(self):
        return [self.collection_identifier, self.key, self.value]

    def __repr__(self):
        return "<{}: {}_{}:={}>".format(
            self.__class__.__name__,
            self.collection_identifier, self.key, self.value
        )

class Conditional(Codeform):
    def __init__(self, condition, consequent, alternative=None):
        super().__init__()
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    @property
    def children(self):
        branches = [self.condition, self.consequent]
        if self.alternative is not None:
            branches.append(self.alternative)
        return branches

    def __repr__(self):
        return "<{}: ({}, {}/{})>".format(
            self.__class__.__name__,
            self.condition, self.consequent, self.alternative
        )

class SingletrackedConditional(Codeform):
    def __init__(self, condition, expressions):
        super().__init__()
        self.condition = condition
        self.expressions = expressions

        self.condition.statementlike = False

    @property
    def children(self):
        return [self.condition] + self.expressions

    def __repr__(self):
        return "<{}: ({}, {}/{})>".format(
            self.__class__.__name__,
            self.condition, self.expressions
        )

class IndeterminateIteration(Codeform):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

        self.condition.statementlike = False

    @property
    def children(self):
        return [self.condition] + self.body

    def __repr__(self):
        return "<{}: [{} {}]>".format(
            self.__class__.__name__,
            self.condition, self.body
        )

class DeterminateIteration(Codeform):
    def __init__(self, index_identifier, iterable, body):
        super().__init__()
        self.index_identifier = index_identifier
        self.iterable = iterable
        self.body = body

        self.index_identifier.statementlike = False
        self.iterable.statementlike = False

    @property
    def children(self):
        # XXX LACK OF THEORETICAL AND ÆSTHETIC INTEGRITY: Considering the index
        # and iterable as "children" in for loops seems a little in tension
        # with not considering function arguments as "children". Which is
        # correct??  If they're not "children" in the "usual" sense, how shall
        # we annotate them?
        #
        # Motivation: the index identifier and iterable should _not_ be
        # statementlike (the Rust backend should not suffix them with a
        # semicolon), but the body expressions _should_. We seem to have
        # successfully hacked around this in our initializer here, but it
        # should be more elegant and graceful.
        return [self.index_identifier, self.iterable] + self.body

    def __repr__(self):
        return "<{}: [{} {}]>".format(
            self.__class__.__name__,
            self.index_identifier, self.iterable
        )

class Application(Expression):
    def __init__(self, function, arguments):
        super().__init__()
        self.function = function
        self.arguments = arguments

    @property
    def children(self):
        return [self.function] + self.arguments

    def __repr__(self):
        return "<{}: ({}, {})>".format(
            self.__class__.__name__,
            self.function.value, ' '.join(repr(arg) for arg in self.arguments)
        )


class Sequential(Expression):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    @property
    def children(self):
        return self.elements

    def __len__(self):
        return len(self.elements)

    def __eq__(self, other):
        if len(self.elements) != len(other.elements):
            return False
        return all(sel == oel for sel, oel
                   in zip(self.elements, other.elements))

    def __repr__(self):
        return "<{}: {}{}{}>".format(
            self.__class__.__name__,
            self.open_delimiter, ' '.join(repr(el) for el in self.elements),
            self.close_delimiter
        )

class List(Sequential):
    mutable = True
    # XXX: are we actually using these bare token string representations
    # anywhere?
    open_delimiter = '['
    close_delimiter = ']'

class Vector(Sequential):
    open_delimiter = close_delimiter = '|'


class Associative(Expression):
    def __init__(self, associations):
        super().__init__()
        self.associations = associations

        self.identifier = None

    @property
    def children(self):
        return self.associations

# Should this inherit from something? A key value pair shouldn't
# really be its own expression independent of any Dictionary or
# Hashtable literal. Could there be an argument for a common
# superclass with Argument and iteration bindings strong than "I don't
# really know what to do with any of these"?
class Association:
    def __init__(self, key, value):
        self.key = key
        self.value = value

        self.statementlike = False
        self.key.statementlike = False
        self.value.statementlike = False

    @property
    def children(self):
        return [self.key, self.value]

    def __repr__(self):
        return "<{}: {} {};>".format(
            self.__class__.__name__, self.key, self.value
        )

class Dictionary(Associative):
    mutable = True
    open_delimiter = '{'
    close_delimiter = '}'

class Hashtable(Associative):
    open_delimiter = '<'
    close_delimiter = '>'


class Atom(Expression):
    def __init__(self, value):
        super().__init__()
        self.value = value

    @property
    def children(self):
        return []

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.value == other.value)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.value)

class IdentifierAtom(Atom):
    ...

class Argument(IdentifierAtom):
    def __init__(self, name, type_specifier):
        self.value = name
        self.type_specifier = type_specifier

class IntegerAtom(Atom):
    ...

class FloatAtom(Atom):
    ...

class StringAtom(Atom):
    ...

class BooleanAtom(Atom):
    ...

class VoidAtom(Atom):
    ...

class PrimitiveAtom(Atom):
    ...

# Maybe??
class DentAtom(Atom):
    ...

class ReservedAtom(Atom):
    ...

class TypeSpecifierAtom(Atom):
    ...

class BuiltinAtom(Atom):
    def __init__(self, value, special=False):
        super().__init__(value)
        self.special = special

class ParsingException(Exception):
    ...


def parse_rest(tokenstream, *, closer, item_parser=None):
    if item_parser is None:
        # because can't supply this as a ordinary default argument if we want
        # this function defined earlier than `parse_expression` while Python is
        # loading this module
        item_parser = parse_expression
    body = []
    done_here = False
    while not done_here:
        next_token = tokenstream.peek()
        if isinstance(next_token, closer):
            tokenstream.pop()
            done_here = True
        else:
            body.append(item_parser(tokenstream))
    return body

def parse_expression_expecting(tokenstream, *, being_instance,
                               further_conditions=None):
    """(`further_conditions` should be a dictionary whose keys are explanations
    and whose values are predicates indicating whether the parsing is OK)"""
    if further_conditions is None:
        further_conditions = {}
    expression = parse_expression(tokenstream)
    if not (isinstance(expression, being_instance) and
            all(condition(expression) for condition
                in further_conditions.values())):
        raise ParsingException("Expected {} such that {}; got {}".format(
            being_instance.__class__.__name__,
            oxford_series(further_conditions.keys()),
            expression))
    return expression

def parse_codeform(tokenstream):
    open_keyword = tokenstream.pop()
    if not isinstance(open_keyword, Keyword):
        raise ParsingException(
            "Expected a keyword token, got {}.".format(open_keyword))

    if open_keyword.representation == "if":
        condition = parse_expression(tokenstream)
        dash = parse_expression_expecting(
            tokenstream,
            being_instance=ReservedAtom,
            further_conditions={'it\'s an em dash': lambda d: d.value == "—"}
        )
        indent = parse_expression_expecting(tokenstream,
                                            being_instance=Indent)
        consequent = parse_expression(tokenstream)
        post_consequent = parse_expression(tokenstream)
        if isinstance(post_consequent, Dedent):
            return Conditional(condition, consequent)
        else:
            alternative = post_consequent
            parse_expression_expecting(tokenstream, being_instance=Dedent)
            return Conditional(condition, consequent, alternative)
    elif open_keyword.representation == "when":
        condition = parse_expression(tokenstream)
        dash = parse_expression_expecting(
            tokenstream,
            being_instance=ReservedAtom,
            further_conditions={'it\'s an em dash': lambda d: d.value == "—"}
        )
        indent = parse_expression_expecting(tokenstream,
                                            being_instance=Indent)
        body = parse_rest(tokenstream, closer=Dedent)
        return SingletrackedConditional(condition, body)
    elif open_keyword.representation == ":=":
        # TODO: same error-checking guarantees throughout this entire (long)
        # `parse_codeform` function
        identifier, identified = [parse_expression(tokenstream)
                                  for _ in range(2)]
        return Definition(identifier, identified)
    elif open_keyword.representation == "_:=":
        collection, subscript, identified = [parse_expression(tokenstream)
                                             for _ in range(3)]
        return SubscriptAssignment(collection, subscript, identified)
    elif open_keyword.representation == ":=λ":
        name = parse_expression(tokenstream)
        argument_sequential = parse_expression(tokenstream)
        _arrow = parse_expression(tokenstream)
        return_type = parse_expression(tokenstream)
        indent = parse_expression(tokenstream)
        body = parse_rest(tokenstream, closer=Dedent)
        return NamedFunctionDefinition(name, argument_sequential, return_type,
                                       body)
    elif open_keyword.representation == "do":
        dash, indent = [parse_expression(tokenstream) for _ in range(2)]
        body = parse_rest(tokenstream, closer=Dedent)
        return DoBlock(body)
    elif open_keyword.representation == "for":
        bindings = parse_expression(tokenstream)
        index_identifier, iterable = bindings.elements
        dash, indent = [parse_expression(tokenstream) for _ in range(2)]
        body = parse_rest(tokenstream, closer=Dedent)
        return DeterminateIteration(index_identifier, iterable, body)
    elif open_keyword.representation == "while":
        condition = parse_expression(tokenstream)
        dash, indent = [parse_expression(tokenstream) for _ in range(2)]
        body = parse_rest(tokenstream, closer=Dedent)
        return IndeterminateIteration(condition, body)
    else:
        raise ParsingException("Expected keyword, got {}".format(open_keyword))

def parse_application(tokenstream):
    open_paren = tokenstream.pop()
    if not isinstance(open_paren, OpenParenthesis):
        raise ParsingException(
            "Expected an open parenthesis token, got {}.".format(open_paren))
    first = parse_expression(tokenstream)
    rest = parse_rest(tokenstream, closer=CloseParenthesis)

    if not isinstance(first, IdentifierAtom):
        raise ParsingException("Expected first element of application to be "
                               "an identifier, got {}".format(first))
    return Application(first, rest)

def parse_sequential(tokenstream):
    open_delimiter = tokenstream.pop()
    if not (isinstance(open_delimiter, SequentialDelimiter) or
            not isinstance(open_delimiter, OpenDelimiter)):
        raise ParsingException("Expected an opening sequential delimiter ('[' "
                               "or '|'), got {}".format(open_delimiter))
    if isinstance(open_delimiter, OpenBracket):
        sequential_class = List
        closer = CloseBracket
    elif isinstance(open_delimiter, Pipe):
        sequential_class = Vector
        closer = Pipe
    elements = parse_rest(tokenstream, closer=closer)
    return sequential_class(elements)

def parse_association(tokenstream):
    key = parse_expression(tokenstream)
    value = parse_expression(tokenstream)
    association_delimiter = tokenstream.pop()
    if not isinstance(association_delimiter, Semicolon):
        raise ParsingException("Expected semicolon to separate associations")
    return Association(key, value)

def parse_associative(tokenstream):
    open_delimiter = tokenstream.pop()
    if not (isinstance(open_delimiter, AssociativeDelimiter) and
            isinstance(open_delimiter, OpenDelimiter)):
        raise ParsingException("Expected an opening associative delimiter ('{{' "
                               "or '<'), got {}".format(open_delimiter))
    if isinstance(open_delimiter, OpenBrace):
        associative_class = Dictionary
        closer = CloseBrace
    # elif isinstance(open_delimiter, ... uh, we need to call the '<' something)
    else:
        raise NotImplementedError("TODO: parse Glitteral hashtables")
    associations = parse_rest(tokenstream,
                              closer=closer, item_parser=parse_association)
    return associative_class(associations)

def parse_expression(tokenstream):
    leading_token = tokenstream.peek()
    logger.debug("leading_token in parse_expression is %s", leading_token)

    if isinstance(leading_token, Keyword):  # indented codeforms
        return parse_codeform(tokenstream)
    elif isinstance(leading_token, OpenDelimiter):  # collections
        if isinstance(leading_token, OpenParenthesis):
            return parse_application(tokenstream)
        elif (isinstance(leading_token, OpenBracket) or
            isinstance(leading_token, Pipe)):
            return parse_sequential(tokenstream)
        elif (isinstance(leading_token, OpenBrace) or
              # still need to name the '<' thingy
              False):
            return parse_associative(tokenstream)
        else:
            raise ParsingException(
                "Failed to advance from opening delimiter {}".format(
                    leading_token))
    else:  # atoms
        expression_token = tokenstream.pop()
        if isinstance(expression_token, Keyword):
            return PrimitiveAtom(expression_token.representation)
        elif isinstance(expression_token, AbstractDent):
            # XXX INCONSISTENCY TODO FIXME RESEARCH: the
            # indent/dedent/aligned-newline tokens don't have representations;
            # rather than recreate parallel boilerplate here, maybe try out
            # letting the token stand for itself?? Distinguishing "atoms" in
            # this module and "tokens" in the lexer seemed like a good idea on
            # the grounds that lexing and parsing are different things, but
            # maybe the token/atom distinction isn't actually buying us very
            # much??
            return expression_token
        elif isinstance(expression_token, TypeSpecifier):
            return TypeSpecifierAtom(expression_token.representation)
        elif isinstance(expression_token, IntegerLiteral):
            return IntegerAtom(int(leading_token.representation))
        elif isinstance(expression_token, FloatLiteral):
            return FloatAtom(float(leading_token.representation))
        elif isinstance(expression_token, StringLiteral):
            return StringAtom(expression_token.representation.strip('"'))
        elif isinstance(expression_token, BooleanLiteral):
            return (BooleanAtom(True)
                    if expression_token.representation == "Truth"
                    else BooleanAtom(False))
        elif isinstance(expression_token, VoidLiteral):
            return VoidAtom(None)
        elif isinstance(expression_token, Identifier):
            return IdentifierAtom(expression_token.representation)
        elif isinstance(expression_token, Reserved):
            return ReservedAtom(expression_token.representation)
        else:
            raise ParsingException("Failed to recognize an expression from "
                                   "{}".format(expression_token))

def parse(tokenstream):
    while True:
        yield parse_expression(tokenstream)
