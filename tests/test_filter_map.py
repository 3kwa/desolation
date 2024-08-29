from functools import partial

from desolation.evaluate import evaluate


def test_greater_than():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        expression="(> 0 1)"
    )
    assert result is True


def test_filter_inline():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        expression="(filter (> 0 x) (1 -1 0 2))"
    )
    assert result == [1, 2]


def test_map_inline():
    import arithmetic as domain

    result = partial(evaluate, domain)(
        expression="(map (add 2 x) (1 -1 0 2))"
    )
    assert result == [3, 1, 2, 4]
