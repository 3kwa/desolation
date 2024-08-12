from collections import namedtuple
from functools import lru_cache

import sexpdata


def expand(expression, context):
    parsed = sexpdata.loads(expression)
    operator = parsed[0].value()
    definition = parse(context).get(operator)
    if definition:
        arity = len(definition.arguments)
        count = len(parsed[1:])
        assert arity == count, f"{operator} arity is {arity} not {count}"

        result = definition.expression[:]

        for argument, substitution in zip(
            definition.arguments, (sexpdata.dumps(argument) for argument in parsed[1:])
        ):
            result = result.replace(argument, substitution)

    else:
        result = expression
        for definition in parse(context).values():
            if len(definition.arguments) == 0:
                result = result.replace(definition.name, definition.expression)

    return result


@lru_cache
def parse(context, *, domain=None):
    result = {}
    for define in sexpdata.parse(context):
        assert (
            define[0].value() == "define"
        ), "context (define (operator *ARGUMENTS) (expression))"

        name = define[1][0].value()
        if domain is not None and name in domain.FUNCTIONS:
            raise ContextError(f"{name} already in domain")
        if name in result:
            raise ContextError(f"{name} not unique")
        arguments = tuple(argument.value() for argument in define[1][1:])
        for symbol in _list_operators_used(define[2]):
            if (
                domain is not None and symbol.value() not in domain.FUNCTIONS.keys()
            ) and symbol.value() not in result:
                raise ContextError(f"{symbol.value()}=?")
        expression = sexpdata.dumps(define[2])
        result[name] = Define(name, arguments, expression)
    return result


Define = namedtuple("Define", "name arguments expression")


class ContextError(Exception):
    pass  # noqa


def _list_operators_used(data):
    # first element of each list
    result = []

    def recursive(item):
        if isinstance(item, list) and item:
            result.append(item[0])
            for sub_item in item:
                recursive(sub_item)

    recursive(data)
    return result
