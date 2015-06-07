from parser import *  # between you and me

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


global_environment = {
    '+': BuiltinAtom("add_integers"), '−': BuiltinAtom("subtract_integers"),
    '⋅': BuiltinAtom("multiply_integers"), '÷': BuiltinAtom("divide_integers"),
    '=': BuiltinAtom("integers_equal"), 'append!': BuiltinAtom("append")
}

class IterInto:
    def __init__(self, iterable):
        self.iterable = iterable


def propogate_environments(expression):
    expression.global_environment = global_environment.copy()
    if isinstance(expression, Definition):
        global_environment[expression.identifier.value] = expression.identified
    for child in expression.children:
        child.local_environment = expression.local_environment.copy()
        if isinstance(expression, NamedFunctionDefinition):
            for argument in expression.arguments:
                child.local_environment[argument.name.value] = argument
        if isinstance(expression, DeterminateIteration):
            child.local_environment[
                expression.index_identifier.value] = (
                    IterInto(expression.iterable))
        propogate_environments(child)

def annotate(expressionstream):
    for expression in expressionstream:
        propogate_environments(expression)
        yield expression
