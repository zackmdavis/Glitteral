from parser import *  # tell it to somepony who cares

logger = logging.getLogger(__name__)
if os.environ.get("GLITTERAL_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


def rustify_type_specifier(type_specifier_atom):
    return {'^int': "isize", '^str': "&str"}.get(type_specifier_atom.value)

def rustify_argument(argument):
    return "{}: {}".format(
        argument.name.value, rustify_type_specifier(argument.type))

def generate_named_function_definition(definition):
    return """fn %s(%s) -> %s {
%s
}
""" % (definition.name.value,
       ', '.join(rustify_argument(arg) for arg in definition.arguments),
       rustify_type_specifier(definition.return_type),
       '\n'.join(
           generate_expression(expression)
           for expression in definition.expressions))

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

def generate_determinate_iteration(iteration):
    return "for &%s in %s.iter() { %s }" % (
        tuple(map(generate_expression,
                  (iteration.index_identifier, iteration.iterable))) +
                   # XXX hideous
                   ('\n'.join(
                       generate_expression(expression)
                       for expression in iteration.body
                   ),)
    )

def generate_application(application):
    return "{}({})".format(
        generate_expression(application.function),  # XX
        ', '.join(generate_expression(arg) for arg in application.arguments)
    )

environment = {'+': "add_integers", '−': "subtract_integers",
               '⋅': "multiply_integers", '÷': "divide_integers"}

def generate_sequential(expression):
    type_to_delimiter = {List: ('vec![', ']'), Vector: ('[', ']')}
    open_delimiter, close_delimiter = type_to_delimiter[expression.__class__]
    return ''.join(
        [open_delimiter,
         ', '.join(generate_expression(element)
                   for element in expression.elements),
         close_delimiter]
    )

def generate_expression(expression):
    global environment
    if isinstance(expression, Codeform):
        if isinstance(expression, NamedFunctionDefinition):
            return generate_named_function_definition(expression)
        elif isinstance(expression, Definition):
            return generate_definition(expression)
        elif isinstance(expression, Conditional):
            return generate_conditional(expression)
        elif isinstance(expression, DeterminateIteration):
            return generate_determinate_iteration(expression)
        elif isinstance(expression, Application):
            return generate_application(expression)
    if isinstance(expression, Sequential):
        return generate_sequential(expression)
    elif isinstance(expression, Atom):
        if isinstance(expression, IdentifierAtom):
            return "{}".format(
                environment.get(expression.value, expression.value))
        elif isinstance(expression, IntegerAtom):
            return "{}isize".format(expression.value)
        elif isinstance(expression, BooleanAtom):
            return "true" if expression.value else "false"
        elif isinstance(expression, StringAtom):
            return '"{}"'.format(expression.value)

def generate_code(expressions):
    logger.debug("expressions for which to generate code: %s", expressions)
    return """
fn add_integers(a: isize, b: isize) -> isize { a + b }
fn subtract_integers(a: isize, b: isize) -> isize { a - b }
fn multiply_integers(a: isize, b: isize) -> isize { a * b }
fn divide_integers(a: isize, b: isize) -> isize { a / b }
fn print_integer(n: isize) { println!(\"{}\", n) }

fn main() {
%s
}
""" % '\n'.join(generate_expression(expression)
                for expression in expressions)
