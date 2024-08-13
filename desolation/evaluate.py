import sexpdata

from .context import parse, expand


def evaluate(domain, *, expression, context=None, **kwargs):
    """
    >>> partial(evaluate, domain)(
    ...     "(mul (add (div a b) c) e)",
    ...     a=1, b=2, c=3, e=5,
    ... )
    17.5
    """
    if context is not None:
        expression = expand(expression, parse(context))
    for key, value in domain.SUBSTITUTIONS.items():
        expression = expression.replace(f" {key} ", f" {value} ")
    return _evaluate(domain, sexpdata.loads(expression), kwargs)


def _evaluate(domain, expression, kwargs):
    try:
        expression[0]
    except TypeError:
        return expression
    try:
        return domain.FUNCTIONS[expression[0].value()](
            *[_evaluate(domain, e, kwargs) for e in expression[1:]]
        )
    except KeyError:
        raise RuntimeError(f"{expression[0].value()}=?")
    except AttributeError:
        pass
    try:
        return kwargs[expression.value()]
    except KeyError:
        raise RuntimeError(f"{expression.value()}=?")


def pretty(expression, *, indent=4):
    functions = 0
    for line in expression.replace(")", " )").split(" "):
        if line.startswith("("):
            print(" " * functions * indent, line)
            functions += 1
        elif line == ")":
            functions -= 1
            print(" " * functions * indent, line)
        else:
            print(" " * functions * indent, line)
