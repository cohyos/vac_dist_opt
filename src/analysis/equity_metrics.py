"""
Equity and public health metrics for vaccine distribution analysis.

Includes Gini coefficient, equity gap, DALYs, and years of life lost.
"""

import numpy as np
from typing import Dict, List


def gini_coefficient(values: np.ndarray) -> float:
    """
    Compute Gini coefficient of inequality.
    0 = perfect equality, 1 = perfect inequality.
    """
    if len(values) == 0 or np.sum(values) == 0:
        return 0.0
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_vals) - (n + 1) * np.sum(sorted_vals)) / (n * np.sum(sorted_vals))


def vaccine_gini(countries: Dict) -> float:
    """
    Compute Gini coefficient of per-capita vaccine distribution.

    Args:
        countries: Dict of {name: EnhancedCountry}
    """
    per_capita = np.array([
        c.compartments.total_vaccinated / c.population if c.population > 0 else 0
        for c in countries.values()
    ])
    return gini_coefficient(per_capita)


def equity_gap(countries: Dict, n_groups: int = 10) -> float:
    """
    Ratio of vaccination rates between top-N and bottom-N GNI countries.

    Returns ratio > 1 means rich countries vaccinated more per capita.
    """
    sorted_countries = sorted(countries.values(), key=lambda c: c.gni_per_capita)
    n = min(n_groups, len(sorted_countries) // 2)
    if n == 0:
        return 1.0

    bottom = sorted_countries[:n]
    top = sorted_countries[-n:]

    bottom_rate = np.mean([c.compartments.total_vaccinated / c.population for c in bottom])
    top_rate = np.mean([c.compartments.total_vaccinated / c.population for c in top])

    if bottom_rate == 0:
        return float('inf') if top_rate > 0 else 1.0
    return top_rate / bottom_rate


def time_to_minimum_coverage(time_series_data: List[Dict], countries: Dict,
                              min_coverage: float = 0.20) -> int:
    """
    Days until the LAST country reaches min_coverage vaccination.
    Returns None if never reached.
    """
    # This would need to be tracked per-country over time
    # For now, check final state
    all_covered = all(
        c.compartments.total_vaccinated / c.population >= min_coverage
        for c in countries.values() if c.population > 0
    )
    if all_covered:
        return len(time_series_data)  # Approximate
    return None


# Age-specific remaining life expectancy (approximate, years)
LIFE_EXPECTANCY_BY_AGE = np.array([65.0, 45.0, 25.0, 13.0, 5.0])


def years_of_life_lost(countries: Dict) -> float:
    """
    Compute total years of life lost (YLL) from deaths,
    weighted by age-specific remaining life expectancy.
    """
    total_yll = 0.0
    for country in countries.values():
        deaths_by_age = country.compartments.D
        total_yll += np.sum(deaths_by_age * LIFE_EXPECTANCY_BY_AGE)
    return total_yll


def dalys_averted(countries_with_vax: Dict, countries_no_vax: Dict) -> float:
    """
    Estimate DALYs averted by vaccination compared to no-vaccination baseline.
    Simplified: DALY = YLL (premature death) + YLD (disability)
    We approximate YLD as 0.1 × YLL for COVID (long COVID contribution)
    """
    yll_vax = years_of_life_lost(countries_with_vax)
    yll_no_vax = years_of_life_lost(countries_no_vax)
    daly_factor = 1.1  # YLD ≈ 10% of YLL
    return (yll_no_vax - yll_vax) * daly_factor
