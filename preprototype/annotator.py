from parser import *  # between you and me

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


global_environment = {
    '+': BuiltinAtom("add_integers"), '−': BuiltinAtom("subtract_integers"),
    '⋅': BuiltinAtom("multiply_integers"), '÷': BuiltinAtom("divide_integers"),
    '=': BuiltinAtom("integers_equal"), 'append!': BuiltinAtom("append"),
    'greater': BuiltinAtom("greater"), 'less': BuiltinAtom("less"),
    'not_greater': BuiltinAtom("not_greater"),
    'not_less': BuiltinAtom("not_less"),
    'range': BuiltinAtom("range"),
    'print_integer': BuiltinAtom("print_integer"),
}

class IterInto:
    def __init__(self, iterable):
        self.iterable = iterable


def propogate_environments(expression, toplevel=False):
    logger.debug("propogating environments for expression %s", expression)

    # Snapshot our running record of the global environment for this node,
    expression.global_environment = global_environment.copy()
    # then modify it if directed.
    if isinstance(expression, Definition):
        global_environment[expression.identifier.value] = expression.identified
    if isinstance(expression, NamedFunctionDefinition):
        global_environment[expression.name.value] = expression

    # "Some" glitteralc backends "may" want to know if an expression is
    # on the top level (not nested within other statements).
    if toplevel:
        expression.toplevel = True

    for child in expression.children:
        # set locals for :=λ, let, for, &c.
        child.local_environment = expression.local_environment.copy()
        if isinstance(expression, NamedFunctionDefinition):
            for argument in expression.arguments:
                child.local_environment[argument.value.value] = argument
        if isinstance(expression, DeterminateIteration):
            child.local_environment[
                expression.index_identifier.value] = (
                    IterInto(expression.iterable))
        # and recurse
        propogate_environments(child)

def annotate(expressionstream):
    for expression in expressionstream:
        propogate_environments(expression, toplevel=True)
        yield expression
