from functools import partial

from desolation.evaluate import evaluate


def test_arithmetic_domain_evaluation():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        expression="(mul (add (div a b) c) e)",
        a=1,
        b=2,
        c=3,
        e=5,
    )
    assert result == 17.5


def test_evaluate_domain_context():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        expression="(cube a)",
        context="""
            (define (square x) (mul x x))
            (define (cube x) (mul x (square x)))
            """,
        a=2,
    )
    assert result == 8
