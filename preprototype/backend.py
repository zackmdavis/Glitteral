from parser import *  # tell it to somepony who cares

def generate_definition(definition):
    return "let {} = {};".format(
        generate_expression(definition.identifier),
        generate_expression(definition.identified)
    )

def generate_conditional(conditional):
    return "if %s { %s } else { %s }" % (
        generate_expression(conditional.condition),
        generate_expression(conditional.consequent),
        generate_expression(conditional.alternative)
    )

def generate_application(application):
    return "{}({})".format(
        generate_expression(application.function),  # XX
        ', '.join(generate_expression(arg) for arg in application.arguments)
    )

environment = {}  # XXX!?

def generate_expression(expression):
    global environment
    if isinstance(expression, Codeform):
        if isinstance(expression, Definition):
            return generate_definition(expression)
        elif isinstance(expression, Conditional):
            return generate_conditional(expression)
        elif isinstance(expression, Application):
            return generate_application(expression)
    elif isinstance(expression, Atom):
        if isinstance(expression, IdentifierAtom):
            return "{}".format(
                environment.get(expression.value, expression.value))
        elif isinstance(expression, IntegerAtom):
            return "{}isize".format(expression.value)
        elif isinstance(expression, StringAtom):
            return '"{}"'.format(expression.value)

def generate_code(expressions):
    return ("fn print_integer(n: isize) { println!(\"{}\", n) }\n"
            "fn main() { %s }" %
            '\n'.join(generate_expression(expression)
                      for expression in expressions))
