import logging
import itertools
import functools
import os

from parser import *  # tell it to somepony who cares
from utils import get_logger

logger = get_logger(__name__)


class CodeGenerationException(Exception):
    ...

class CodeGenerationNotImplementedException(
        NotImplementedError, CodeGenerationException):
    ...


autoidentifier_sequence = (
    "_gltrl_autoidentifier_{}".format(i) for i in itertools.count(1))


def rustify_type_specifier(type_specifier_atom):
    return {'^int': "isize", '^float': "f64",
            '^str': "&str", '^bool': "bool",
            '^[int]': "&mut Vec<isize>", None: "()"}[type_specifier_atom.value]

def rustify_argument(argument):
    return "{}: {}".format(
        argument.value.value, rustify_type_specifier(argument.type_specifier))

def condescend_to_ascii(identifier):
    replacements = {'!': "_bang_", '?': "_question_"}
    return functools.reduce(
        lambda s, bad_ok: s.replace(*bad_ok),
        replacements.items(),
        identifier
    )

def semicolon_if_statementlike(expression):
    return ';' if getattr(expression, 'statementlike') else ''

def generate_named_function_definition(definition):
    return """fn %s(%s) -> %s {
%s
}
""" % (condescend_to_ascii(definition.name.value),
       ', '.join(rustify_argument(arg) for arg in definition.arguments),
       rustify_type_specifier(definition.return_type),
       '\n'.join(
           generate_expression(expression)
           for expression in definition.expressions))

def generate_do_block(block):
    return "{ %s }" % "\n".join(
        generate_expression(expression) for expression in block.expressions)

def generate_definition(definition):
    return "{}{} = {}{}".format(
        ("let mut " if not definition.environment.get(
            definition.identifier.value) else ''),
        condescend_to_ascii(definition.identifier.value),
        generate_expression(definition.identified),
        # XXX this is really genuinely awful (but the idea is that at the
        # moment, associatives are the only kind of AST node whose
        # instantitation needs to be spread over multiple Rust statements, so
        # it's convenient for `generate_associative` to supply its own
        # semicolons, whereas for other, more locally-contained, identifiables,
        # we'll supply the semicolon here).
        ';' if not isinstance(definition.identified, Associative) else ''
    )

def generate_subscript_assignment(assignment):
    return "{}[{} as usize] = {};".format(
        assignment.collection_identifier.value,
        assignment.key.value,  # XXX: I'm overusing the word "value"
        generate_expression(assignment.value)
    )

def generate_conditional(conditional):
    branches = "if %s { %s }" % (
        generate_expression(conditional.condition),
        generate_expression(conditional.consequent)
    )
    if conditional.alternative is not None:
        branches += " else { %s }" % generate_expression(conditional.alternative)
    return branches

def generate_singletracked_conditional(one_conditional):
    return "if %s { %s }" % (
        generate_expression(one_conditional.condition),
        '\n'.join(
            generate_expression(expression)
            for expression in one_conditional.expressions
        )
    )

def generate_indeterminate_iteration(iteration):
    return ("""while %s {
%s
}""" % (generate_expression(iteration.condition),
        '\n'.join(generate_expression(expression)
                  for expression in iteration.body)))

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

def generate_special_builtin_dispatched_application(application):
    # XXX this function and everything around it is dreadful in more ways than
    # one
    if (application.environment.get(application.function.value).value ==
        "get_subscript"):
        container_identifier, key_identifier = application.arguments
        container = application.environment.get(container_identifier.value)
        if isinstance(container, List) or (
                # XXX MORE GRATUITOUS COMPLEXITY: we've been treating function
                # parameters differently (wrapped up in an Argument)
                isinstance(container, Argument) and
                container.type_specifier.value[:2] == "^["):
            underfunction = "list_get_subscript"
        elif isinstance(container, Vector):
            underfunction = "vector_get_subscript"
            raise CodeGenerationException("TODO make vectors work")
        elif isinstance(container, Dictionary) or (
                isinstance(container, Argument) and
                container.type_specifier.value[:2] == "^{"):
            underfunction = "str_int_dictionary_get_subscript"
        else:
            raise CodeGenerationException("_ called with first argument {}, "
                                          "expected Container "
                                          "type".format(container))
        return "{}({}){}".format(
            underfunction,
            ', '.join(generate_expression(arg)
                      for arg in application.arguments),
            semicolon_if_statementlike(application)
        )

    elif (application.environment.get(application.function.value).value ==
          "comprehend"):
        # SCRAP: I'm losing hope that this is going to work at all, even in the
        # manner of desperate hacks that I have been known to make work with a
        # sufficient amount of applied desperate effort
        container, bindings, item = application.arguments
        if not isinstance(container, List):
            raise CodeGenerationNotImplementedException("TODO")
        index_identifier, iterable = bindings.elements
        index_identifier.local_environment[
            index_identifier.value] = "✓"  # lies, depravity, and deception
        item.local_environment[index_identifier.value] = "✓"
        container_identifier = IdentifierAtom(next(autoidentifier_sequence))
        container_identifier.local_environment[
            container_identifier.value] = "✓"

        # XXX I feel like if the Doctrine of Separatation of Concerns were here,
        # she would say that we really shouldn't be generating new AST nodes in
        # this module, which is supposed to just be about "generating code"
        # (whatever that means)!  But if I don't know enough to rearchitect the
        # world yet, I feel better about at least not duplicating for-loop
        # generation
        container_autodefinition = Definition(
            container_identifier,
            container)
        append_bang = IdentifierAtom("append!")
        append_bang.global_environment['append!'] = BuiltinAtom("append")
        comprehending_iteration = DeterminateIteration(
            index_identifier, iterable,
            [Application(append_bang,
                         [container_identifier, item])]
        )
        # XXX this is, uh, cute, I guess, but how to we actually refer to the
        # value that we just autogenerated a name for, huh??
        return '\n'.join([generate_expression(container_autodefinition),
                          generate_expression(comprehending_iteration)])

def generate_application(application):
    if getattr(application.environment.get(application.function.value),
               'special', None):
        return generate_special_builtin_dispatched_application(application)
    return "{}({}){}".format(
        generate_expression(application.function),  # XX
        ', '.join(generate_expression(arg) for arg in application.arguments),
        semicolon_if_statementlike(application)
    )

def generate_sequential(sequential):
    type_to_delimiter = {List: ('vec![', ']'), Vector: ('[', ']')}
    open_delimiter, close_delimiter = type_to_delimiter[type(sequential)]
    return ''.join(
        [open_delimiter,
         ', '.join(generate_expression(element)
                   for element in sequential.elements),
         close_delimiter]
    ) + semicolon_if_statementlike(sequential)

def generate_associative(associative):
    # TODO: what is our strategy going to be for Glitteral
    # (immuatable) Hashtables?
    return "HashMap::new();\n{}\n".format(
        '\n'.join(
            "{}.insert({}, {});".format(
                generate_expression(associative.identifier),
                generate_expression(association.key),
                generate_expression(association.value))
            for association in associative.associations
        )
    )

def represent_identifiable(identifier):
    try:
        identified = identifier.environment[identifier.value]
    except KeyError as e:
        raise CodeGenerationException(
            "{} not found in environment".format(identifier.value)) from e
    if isinstance(identified, BuiltinAtom):
        return "{}{}".format(identified.value,
                             semicolon_if_statementlike(identifier))
    else:
        underidentifier = condescend_to_ascii(identifier.value)
        if getattr(identified, "mutable", None):
            return "&mut {}{}".format(underidentifier,
                                      semicolon_if_statementlike(identifier))
        else:
            return "{}{}".format(underidentifier,
                                 semicolon_if_statementlike(identifier))

def generate_expression(expression):
    if isinstance(expression, Codeform):
        if isinstance(expression, NamedFunctionDefinition):
            return generate_named_function_definition(expression)
        elif isinstance(expression, DoBlock):
            return generate_do_block(expression)
        elif isinstance(expression, Definition):
            return generate_definition(expression)
        elif isinstance(expression, SubscriptAssignment):
            return generate_subscript_assignment(expression)
        elif isinstance(expression, Conditional):
            return generate_conditional(expression)
        elif isinstance(expression, SingletrackedConditional):
            return generate_singletracked_conditional(expression)
        elif isinstance(expression, IndeterminateIteration):
            return generate_indeterminate_iteration(expression)
        elif isinstance(expression, DeterminateIteration):
            return generate_determinate_iteration(expression)
        else:
            raise CodeGenerationException(
                "Couldn't generate code for alleged "
                "Codeform {}".format(expression))
    elif isinstance(expression, Application):
        return generate_application(expression)
    elif isinstance(expression, Sequential):
        return generate_sequential(expression)
    elif isinstance(expression, Associative):
        return generate_associative(expression)
    elif isinstance(expression, Atom):
        if isinstance(expression, IdentifierAtom):
            return represent_identifiable(expression)
        elif isinstance(expression, IntegerAtom):
            return "{}isize{}".format(expression.value,
                                      semicolon_if_statementlike(expression))
        elif isinstance(expression, FloatAtom):
            return "{}f64{}".format(expression.value,
                                      semicolon_if_statementlike(expression))
        elif isinstance(expression, BooleanAtom):
            return ("true{}" if expression.value else "false{}").format(
                semicolon_if_statementlike(expression))
        elif isinstance(expression, VoidAtom):
            return "(){}".format(semicolon_if_statementlike(expression))
        elif isinstance(expression, StringAtom):
            return '"{}{}"'.format(expression.value,
                                   semicolon_if_statementlike(expression))
        else:
            raise CodeGenerationException("Couldn't generate code for alleged "
                                          "atom {}".format(expression))
    else:
        raise CodeGenerationException("Couldn't generate code for alleged "
                                      "expression {}".format(expression))

def generate_code(expressions):
    with open(
            os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)),
                "builtins.rs")) as builtins_rs:
        prelude = builtins_rs.read()
    return """%s

fn main() {
%s
}
""" % (
    prelude,
    '\n'.join(generate_expression(expression)
              for expression in expressions)
)
