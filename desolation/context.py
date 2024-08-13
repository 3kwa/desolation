from collections import namedtuple
from functools import lru_cache

import sexpdata


def expand(expression, definitions={}):
    def expand_recursive(expr):
        if isinstance(expr, list) and expr:
            operator = expr[0].value()
            definition = definitions.get(operator)

            if definition:
                arity = len(definition.arguments)
                count = len(expr) - 1
                assert arity == count, f"{operator} arity is {arity} not {count}"

                result = sexpdata.loads(definition.expression)
                for arg, sub in zip(definition.arguments, expr[1:]):
                    result = replace_symbol(result, arg, expand_recursive(sub))

                return result
            else:
                return [expand_recursive(subexpr) for subexpr in expr]
        elif isinstance(expr, sexpdata.Symbol):
            zero_arg_def = next(
                (
                    d
                    for d in definitions.values()
                    if d.name == expr.value() and not d.arguments
                ),
                None,
            )
            if zero_arg_def:
                return expand_recursive(sexpdata.loads(zero_arg_def.expression))
            return expr
        else:
            return expr

    def replace_symbol(expr, symbol, replacement):
        if isinstance(expr, list):
            return [replace_symbol(subexpr, symbol, replacement) for subexpr in expr]
        elif isinstance(expr, sexpdata.Symbol) and expr.value() == symbol:
            return replacement
        else:
            return expr

    parsed = sexpdata.loads(expression)
    expanded = expand_recursive(parsed)
    return sexpdata.dumps(expanded)


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
        expression = expand(sexpdata.dumps(define[2]), result)
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
