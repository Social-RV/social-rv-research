import math

import pytest

from social_rv_research.judge_stats import (
    binomial_upper_tail,
    compare_paired_binary,
    continuity_corrected_normal_upper_tail,
    cumulative_binary_p_values,
    summarize_top_k,
)


def test_exact_binomial_upper_tail() -> None:
    assert binomial_upper_tail(3, 3) == pytest.approx(0.125)
    assert binomial_upper_tail(0, 3) == 1.0


def test_continuity_corrected_normal_upper_tail() -> None:
    expected = 0.5 * math.erfc((-0.5 / math.sqrt(2.5)) / math.sqrt(2))
    assert continuity_corrected_normal_upper_tail(5, 10) == pytest.approx(expected)


def test_top_k_summary_separates_missing_and_invalid_ranks() -> None:
    summary = summarize_top_k([1, 3, 5, 6, 10, None, -1, 11])

    assert summary.total_input == 8
    assert summary.valid_count == 5
    assert summary.missing_count == 1
    assert summary.invalid_count == 2
    assert summary.counts == {1: 1, 3: 2, 5: 3}
    assert summary.rates[5] == pytest.approx(0.6)


def test_cumulative_checkpoints_match_twenty_chunk_shape() -> None:
    points = cumulative_binary_p_values([True] * 15_368)

    assert [point.observations for point in points] == [
        1_538,
        2_307,
        3_076,
        3_845,
        4_614,
        5_383,
        6_152,
        6_921,
        7_690,
        8_459,
        9_228,
        9_997,
        10_766,
        11_535,
        12_304,
        13_073,
        13_842,
        14_611,
        15_368,
    ]


def test_paired_comparison_uses_exact_mcnemar_test() -> None:
    comparison = compare_paired_binary(
        [True, True, True, False],
        [False, False, False, False],
    )

    assert comparison.left_only == 3
    assert comparison.right_only == 0
    assert comparison.left_minus_right == pytest.approx(0.75)
    assert comparison.mcnemar_p_two_sided == pytest.approx(0.25)


def test_paired_comparison_rejects_different_lengths() -> None:
    with pytest.raises(ValueError, match="equal length"):
        compare_paired_binary([True], [True, False])
