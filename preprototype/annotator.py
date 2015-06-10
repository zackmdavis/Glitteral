import logging
import os

from parser import *  # between you and me

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


global_environment = {
    '+': BuiltinAtom("add_integers"), '−': BuiltinAtom("subtract_integers"),
    '⋅': BuiltinAtom("multiply_integers"), '÷': BuiltinAtom("divide_integers"),
    '=': BuiltinAtom("integers_equal"), '≠': BuiltinAtom("integers_not_equal"),

    'append!': BuiltinAtom("append"), 'length': BuiltinAtom("length"),
    'greater?': BuiltinAtom("greater"), 'less?': BuiltinAtom("less"),
    'not_greater?': BuiltinAtom("not_greater"),
    'not_less?': BuiltinAtom("not_less"),
    'range': BuiltinAtom("range"),

    # TODO: variadics?
    # TODO: unify prints (glitteralc should be smart enough to
    # dispatch on type, or builtins.rs might be able to do something
    # with traits?)
    'print': BuiltinAtom("print"),
    'println': BuiltinAtom("println"),
    'println_container': BuiltinAtom("println_container"),
    'input': BuiltinAtom("input"),
    '&': BuiltinAtom("and"),
    '∨': BuiltinAtom("or"),

    # The Rust backend can naively implement some builtin functions as
    # prewritten Rust functions, but might need to do something
    # cleverer for builtins with polymorphic arguments or other cases
    # where Glitteral wants different semantics (or can we smooth over
    # some of this with traits??) ...
    '_': BuiltinAtom("get_subscript", special=True),
}

class IterInto:
    def __init__(self, iterable):
        self.iterable = iterable


def propogate_environments(expression, statementlike=True):
    logger.debug("propogating environments for %sstatementlike expression %s",
                 'non-' if not statementlike else '', expression)

    if expression.statementlike is None:
        expression.statementlike = statementlike

    # Snapshot our running record of the global environment for this node,
    expression.global_environment = global_environment.copy()
    # then modify it if directed.
    if isinstance(expression, Definition):
        global_environment[expression.identifier.value] = expression.identified
    if isinstance(expression, NamedFunctionDefinition):
        global_environment[expression.name.value] = expression

    for i, child in enumerate(expression.children):
        # set locals for :=λ, let, for, &c.
        child.local_environment = expression.local_environment.copy()
        if isinstance(expression, NamedFunctionDefinition):
            for argument in expression.arguments:
                child.local_environment[argument.value.value] = argument
        elif isinstance(expression, DeterminateIteration):
            child.local_environment[
                expression.index_identifier.value] = (
                    IterInto(expression.iterable))

        # "Some" Glitteral backends will require associative nodes to
        # know what identifier they've been assigned to (if any).
        if (isinstance(expression, Definition) and
            isinstance(child, Associative)):
            child.identifier = expression.identifier

        child_is_statementlike = (
            (i+1 != len(expression.children)) and
            (not (isinstance(expression, Conditional) or
                  isinstance(expression, Application) or
                  isinstance(expression, Sequential) or
                  isinstance(expression, Associative))))
        propogate_environments(child, statementlike=child_is_statementlike)

def annotate(expressionstream):
    for expression in expressionstream:
        propogate_environments(expression, statementlike=True)
        yield expression
