#! /usr/bin/env python
def fuzzy_string_comparison(
    left,
    right,
):
    """remove spaces and make lower case
    returns float 0.0 to 1.0 with 1.0 being correct

    starting at 1.0 check if the characters are the same
    deduct points based on how far apart they are
    """
    _left = normalize_string(left)
    _right = normalize_string(right)
    distance = get_string_distance(_left, _right)

    score = 1.0
    score -= distance / len(_left)
    return score


def normalize_string(_string):
    _string = _string.lower()
    _string = _string.replace(" ", "")
    return _string


def get_string_distance(_left, _right):
    distance = 0
    for i, char in enumerate(_left):
        if i >= len(_right):
            break
        if char != _right[i]:
            distance += 1
    return distance


def _test_perfect_match():
    left = "hello world"
    right = "hello world"
    assert fuzzy_string_comparison(left, right) == 1.0


def _test_fails():
    left = "what"
    right = "zero"
    assert fuzzy_string_comparison(left, right) <= 0.001


def run_test():
    funcs = [
        _test_perfect_match,
        _test_fails,
    ]

    for func in funcs:
        try:
            func()
            print(f"Passed: {func.__name__}")
        except AssertionError:
            print(f"Failed: {func.__name__}")


if __name__ == "__main__":
    run_test()
