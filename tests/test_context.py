import pytest

from desolation.context import parse, Define, ContextError

import arithmetic as domain


def test_parse_single_context():
    context = """
    ; a function that does nothing
    (define (nothing a) (sub (add a 2) 2))
    """
    result = parse(context)
    assert result["nothing"] == Define("nothing", ("a",), "(sub (add a 2) 2)")


def test_parse_many_context():
    context = """
    ; square of x
    (define (square x) (mul x x))
    ; cube of x
    (define (cube x) (mul x (mul x x)))
    """
    result = parse(context)
    assert sorted(result.keys()) == ["cube", "square"]


def test_redefine_from_domain():
    context = """
    (define (sub x) (add x x))
    """
    with pytest.raises(ContextError):
        parse(context, domain=domain)


def test_repeated_parse_context():
    context = """
    ; square of x
    (define (square x) (mul x x))
    ; cube of x
    (define (cube x) (mul x (mul x x)))
    ; cube of x
    (define (cube x) (mul x (square x)))
    """
    with pytest.raises(ContextError):
        parse(context)


def test_define_using_function_in_context():
    context = """
    ; square of x
    (define (square x) (mul x x))
    ; cube of x
    (define (cube x) (mul x (square x)))
    """
    result = parse(context)
    assert result["cube"] == Define("cube", ("x",), "(mul x (mul x x))")


def test_validate_expression_uses_operators_in_domain():
    context = """
    (define (invalid x) (exp x))
    """
    with pytest.raises(ContextError):
        parse(context, domain=domain)


def test_validate_expression_uses_operators_in_domain_or_in_context():
    context = """
    ; square of x
    (define (square x) (mul x x))
    ; cube of x
    (define (cube x) (mul x (square x)))
    """
    parse(context, domain=domain)
