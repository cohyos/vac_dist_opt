"""Needs-based and COVAX-like vaccine allocation strategies."""

import numpy as np
from typing import Dict
from src.strategies.base_strategy import AllocationStrategy


class InfectionRateBased(AllocationStrategy):
    """Prioritize countries with highest current infection rates."""

    @property
    def name(self) -> str:
        return "infection_rate_based"

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        if not countries:
            return {}

        # Weight by infection rate
        infection_rates = {}
        for name, country in countries.items():
            pop = country.compartments.total_population
            inf = country.compartments.total_infected
            infection_rates[name] = inf / pop if pop > 0 else 0

        total_rate = sum(infection_rates.values())
        if total_rate == 0:
            # If no infections, distribute proportionally to population
            total_pop = sum(c.population for c in countries.values())
            weights = {name: c.population / total_pop for name, c in countries.items()}
        else:
            weights = {name: rate / total_rate for name, rate in infection_rates.items()}

        allocations = {}
        for name, country in countries.items():
            share = int(available_vaccines * weights[name])
            capped = min(share, country.max_daily_vaccines(), country.compartments.total_susceptible)
            allocations[name] = capped

        return allocations


class COVAXLike(AllocationStrategy):
    """
    COVAX-style allocation: ensure minimum floor coverage for all countries
    before any country gets surplus allocation.

    Phase 1: Allocate to bring every country to floor_coverage
    Phase 2: Distribute remainder proportionally to population
    """

    def __init__(self, floor_coverage: float = 0.20):
        self.floor_coverage = floor_coverage

    @property
    def name(self) -> str:
        return "covax_like"

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        if not countries:
            return {}

        allocations = {name: 0 for name in countries}
        remaining = available_vaccines

        # Phase 1: Floor allocation
        for name, country in countries.items():
            if remaining <= 0:
                break
            current_coverage = country.compartments.total_vaccinated / country.population
            if current_coverage < self.floor_coverage:
                needed = int((self.floor_coverage - current_coverage) * country.population)
                capped = min(needed, remaining, country.max_daily_vaccines())
                allocations[name] = capped
                remaining -= capped

        # Phase 2: Proportional allocation of remainder
        if remaining > 0:
            total_pop = sum(c.population for c in countries.values())
            for name, country in countries.items():
                share = int(remaining * (country.population / total_pop))
                cap = country.max_daily_vaccines() - allocations[name]
                sus = country.compartments.total_susceptible - allocations[name]
                extra = min(share, max(0, cap), max(0, sus))
                allocations[name] += extra

        return allocations


class MortalityRiskBased(AllocationStrategy):
    """Prioritize countries with highest projected mortality risk."""

    @property
    def name(self) -> str:
        return "mortality_risk_based"

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        if not countries:
            return {}

        # Compute mortality risk score: infected × mortality_rate × (1 / healthcare_capacity)
        risk_scores = {}
        for name, country in countries.items():
            infected = country.compartments.total_infected
            hosp = country.compartments.total_hospitalized
            capacity = country.population * country.epidemic_params.hospital_beds_per_capita
            overload = max(1.0, hosp / capacity) if capacity > 0 else 2.0
            risk_scores[name] = infected * overload

        total_risk = sum(risk_scores.values())
        if total_risk == 0:
            total_pop = sum(c.population for c in countries.values())
            weights = {name: c.population / total_pop for name, c in countries.items()}
        else:
            weights = {name: score / total_risk for name, score in risk_scores.items()}

        allocations = {}
        for name, country in countries.items():
            share = int(available_vaccines * weights[name])
            capped = min(share, country.max_daily_vaccines(), country.compartments.total_susceptible)
            allocations[name] = capped

        return allocations
