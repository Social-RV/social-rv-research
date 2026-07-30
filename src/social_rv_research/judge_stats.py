"""Statistical helpers for auditing blind decoy-judge evaluations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class TopKSummary:
    """Coverage and top-k counts for a fixed candidate-set size."""

    candidate_count: int
    total_input: int
    valid_count: int
    missing_count: int
    invalid_count: int
    counts: dict[int, int]
    rates: dict[int, float]


@dataclass(frozen=True)
class CumulativePValue:
    """One cumulative checkpoint in an ordered binary outcome sequence."""

    observations: int
    successes: int
    p_value: float


@dataclass(frozen=True)
class PairedBinaryComparison:
    """Transition counts and an exact paired test for two binary pipelines."""

    pairs: int
    both_success: int
    left_only: int
    right_only: int
    neither_success: int
    left_rate: float
    right_rate: float
    left_minus_right: float
    mcnemar_p_two_sided: float


def _validate_binomial(successes: int, trials: int, probability: float) -> None:
    if trials < 0:
        raise ValueError("trials must be non-negative")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be between zero and trials")
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between zero and one")


def binomial_upper_tail(successes: int, trials: int, probability: float = 0.5) -> float:
    """Return ``P(X >= successes)`` for ``X ~ Binomial(trials, probability)``."""

    _validate_binomial(successes, trials, probability)
    if successes == 0 or probability == 1:
        return 1.0
    if probability == 0:
        return 0.0

    log_term = (
        math.lgamma(trials + 1)
        - math.lgamma(successes + 1)
        - math.lgamma(trials - successes + 1)
        + successes * math.log(probability)
        + (trials - successes) * math.log1p(-probability)
    )
    term = math.exp(log_term)
    result = term
    odds = probability / (1 - probability)
    for value in range(successes, trials):
        term *= (trials - value) / (value + 1) * odds
        result += term
    return min(1.0, result)


def continuity_corrected_normal_upper_tail(
    successes: int,
    trials: int,
    probability: float = 0.5,
) -> float:
    """Approximate a one-tailed binomial p-value with continuity correction."""

    _validate_binomial(successes, trials, probability)
    if trials == 0:
        raise ValueError("trials must be positive")
    if probability in {0, 1}:
        return binomial_upper_tail(successes, trials, probability)

    variance = trials * probability * (1 - probability)
    z_score = (successes - 0.5 - trials * probability) / math.sqrt(variance)
    return 0.5 * math.erfc(z_score / math.sqrt(2))


def summarize_top_k(
    ranks: Iterable[int | None],
    *,
    candidate_count: int = 10,
    thresholds: Sequence[int] = (1, 3, 5),
) -> TopKSummary:
    """Summarize valid ranks without silently converting missing values to losses."""

    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")
    normalized_thresholds = tuple(sorted(set(thresholds)))
    if not normalized_thresholds or normalized_thresholds[0] < 1:
        raise ValueError("thresholds must contain positive integers")
    if normalized_thresholds[-1] > candidate_count:
        raise ValueError("thresholds cannot exceed candidate_count")

    values = list(ranks)
    valid = [rank for rank in values if isinstance(rank, int) and 1 <= rank <= candidate_count]
    missing_count = sum(rank is None for rank in values)
    invalid_count = len(values) - len(valid) - missing_count
    counts = {
        threshold: sum(rank <= threshold for rank in valid)
        for threshold in normalized_thresholds
    }
    rates = {
        threshold: count / len(valid) if valid else math.nan
        for threshold, count in counts.items()
    }
    return TopKSummary(
        candidate_count=candidate_count,
        total_input=len(values),
        valid_count=len(valid),
        missing_count=missing_count,
        invalid_count=invalid_count,
        counts=counts,
        rates=rates,
    )


def cumulative_binary_p_values(
    outcomes: Iterable[bool],
    *,
    probability: float = 0.5,
    checkpoint_chunks: int = 20,
    minimum_chunks: int = 2,
) -> list[CumulativePValue]:
    """Compute cumulative p-values at stable, evenly spaced checkpoints.

    The chunk size is rounded up. For 15,368 observations, 20 chunks and a
    two-chunk minimum produce 1,538, 2,307, ..., 14,611, and 15,368.
    """

    values = [bool(value) for value in outcomes]
    if not values:
        return []
    if checkpoint_chunks < 1:
        raise ValueError("checkpoint_chunks must be positive")
    if minimum_chunks < 1:
        raise ValueError("minimum_chunks must be positive")

    chunk_size = math.ceil(len(values) / checkpoint_chunks)
    first_checkpoint = minimum_chunks * chunk_size
    checkpoints = list(range(first_checkpoint, len(values), chunk_size))
    if not checkpoints or checkpoints[-1] != len(values):
        checkpoints.append(len(values))

    cumulative_successes = 0
    checkpoint_set = set(checkpoints)
    results: list[CumulativePValue] = []
    for index, outcome in enumerate(values, start=1):
        cumulative_successes += outcome
        if index in checkpoint_set:
            results.append(
                CumulativePValue(
                    observations=index,
                    successes=cumulative_successes,
                    p_value=continuity_corrected_normal_upper_tail(
                        cumulative_successes,
                        index,
                        probability,
                    ),
                )
            )
    return results


def compare_paired_binary(
    left: Iterable[bool],
    right: Iterable[bool],
) -> PairedBinaryComparison:
    """Compare paired binary outcomes with an exact two-sided McNemar test."""

    left_values = [bool(value) for value in left]
    right_values = [bool(value) for value in right]
    if len(left_values) != len(right_values):
        raise ValueError("paired inputs must have equal length")
    if not left_values:
        raise ValueError("paired inputs must not be empty")

    both = sum(a and b for a, b in zip(left_values, right_values))
    left_only = sum(a and not b for a, b in zip(left_values, right_values))
    right_only = sum(not a and b for a, b in zip(left_values, right_values))
    neither = len(left_values) - both - left_only - right_only
    discordant = left_only + right_only
    if discordant == 0:
        p_value = 1.0
    else:
        smaller = min(left_only, right_only)
        lower_tail = binomial_upper_tail(discordant - smaller, discordant, 0.5)
        p_value = min(1.0, 2 * lower_tail)

    left_rate = (both + left_only) / len(left_values)
    right_rate = (both + right_only) / len(right_values)
    return PairedBinaryComparison(
        pairs=len(left_values),
        both_success=both,
        left_only=left_only,
        right_only=right_only,
        neither_success=neither,
        left_rate=left_rate,
        right_rate=right_rate,
        left_minus_right=left_rate - right_rate,
        mcnemar_p_two_sided=p_value,
    )
