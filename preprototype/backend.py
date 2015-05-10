from parser import *  # tell it to somepony who cares

def generate_definition(definition):
    return "let {} = {};".format(
        generate_code(definition.identifier),
        generate_code(definition.identified)
    )

def generate_conditional(conditional):
    return "if %s { %s } else { %s }" % (
        generate_code(conditional.condition),
        generate_code(conditional.consequent),
        generate_code(conditional.alternative)
    )

def generate_application(application):
    return "{}({})".format(
        generate_code(application.function),  # XX
        ', '.join(generate_code(arg) for arg in application.arguments)
    )

def generate_code(expression):
    if isinstance(expression, Codeform):
        if isinstance(expression, Definition):
            return generate_definition(expression)
        elif isinstance(expression, Conditional):
            return generate_conditional(expression)
        elif isinstance(expression, Application):
            return generate_application(expression)
    elif isinstance(expression, Atom):
        if isinstance(expression, IdentifierAtom):
            return "{}".format(expression.value)
        elif isinstance(expression, IntegerAtom):
            return "{}isize".format(expression.value)
        elif isinstance(expression, StringAtom):
            return '"{}"'.format(expression.value)
