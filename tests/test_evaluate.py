from functools import partial

from desolation.evaluate import evaluate


def test_arithmetic_domain_evaluation():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        "(mul (add (div a b) c) e)",
        a=1,
        b=2,
        c=3,
        e=5,
    )
    assert result == 17.5
