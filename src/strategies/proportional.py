"""Proportional and priority-based vaccine allocation strategies."""

import numpy as np
from typing import Dict, List, Tuple
from src.strategies.base_strategy import AllocationStrategy


class PopulationProportional(AllocationStrategy):
    """Allocate vaccines proportional to population."""

    @property
    def name(self) -> str:
        return "population_proportional"

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        total_pop = sum(c.population for c in countries.values())
        if total_pop == 0:
            return {name: 0 for name in countries}

        allocations = {}
        remaining = available_vaccines
        for name, country in countries.items():
            share = int(available_vaccines * (country.population / total_pop))
            capped = min(share, country.max_daily_vaccines(), country.compartments.total_susceptible)
            allocations[name] = capped
            remaining -= capped

        return allocations


class PriorityWeightedStrategy(AllocationStrategy):
    """
    Allocate vaccines with priority weighting (not sequential all-or-nothing).

    Uses a softmax-like weighting so high-priority countries get more but
    all countries get some allocation.
    """

    def __init__(self, sort_key, reverse: bool = True, strategy_name: str = "priority"):
        self._sort_key = sort_key
        self._reverse = reverse
        self._name = strategy_name

    @property
    def name(self) -> str:
        return self._name

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        if not countries:
            return {}

        # Compute priority scores
        scores = {}
        for name, country in countries.items():
            scores[name] = self._sort_key(country)

        # Normalize scores to weights (softmax-like)
        values = np.array(list(scores.values()), dtype=float)
        if self._reverse:
            # Higher value = higher priority
            weights = values / values.sum() if values.sum() > 0 else np.ones(len(values)) / len(values)
        else:
            # Lower value = higher priority (invert)
            if values.min() > 0:
                inv = 1.0 / values
            else:
                inv = 1.0 / (values + 1)
            weights = inv / inv.sum()

        # Allocate proportional to weights, capped by absorption capacity
        allocations = {}
        for (name, country), w in zip(countries.items(), weights):
            share = int(available_vaccines * w)
            capped = min(share, country.max_daily_vaccines(), country.compartments.total_susceptible)
            allocations[name] = capped

        return allocations


# Pre-built priority strategies
def large_population_first():
    return PriorityWeightedStrategy(
        lambda c: c.population, reverse=True, strategy_name="large_population_first"
    )

def small_population_first():
    return PriorityWeightedStrategy(
        lambda c: c.population, reverse=False, strategy_name="small_population_first"
    )

def high_gdp_first():
    return PriorityWeightedStrategy(
        lambda c: c.gni, reverse=True, strategy_name="high_gdp_first"
    )

def low_gdp_first():
    return PriorityWeightedStrategy(
        lambda c: c.gni, reverse=False, strategy_name="low_gdp_first"
    )

def high_gni_first():
    return PriorityWeightedStrategy(
        lambda c: c.gni_per_capita, reverse=True, strategy_name="high_gni_first"
    )

def low_gni_first():
    return PriorityWeightedStrategy(
        lambda c: c.gni_per_capita, reverse=False, strategy_name="low_gni_first"
    )
