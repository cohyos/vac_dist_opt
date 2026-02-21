"""
Vaccination state model with dose scheduling, delayed immunity,
absorption capacity, and hesitancy.
"""

import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Dict, Tuple

from src.models.epidemic_model import NUM_AGE_GROUPS, AGE_GROUPS


@dataclass
class VaccinationParams:
    """Parameters for vaccination mechanics."""
    dose_interval: int = 21          # Days between dose 1 and dose 2
    immunity_delay_dose1: int = 14   # Days after dose 1 for partial immunity
    immunity_delay_dose2: int = 7    # Days after dose 2 for full immunity
    efficacy_dose1: float = 0.52     # Partial efficacy after dose 1
    efficacy_dose2: float = 0.95     # Full efficacy after dose 2
    max_daily_fraction: float = 0.005  # Max fraction of population vaccinated per day


class VaccinationState:
    """Tracks vaccination progress for a single country with dose scheduling."""

    def __init__(self, population: int, gni_per_capita: float,
                 params: VaccinationParams = None):
        self.params = params or VaccinationParams()
        self.population = population
        self.gni_per_capita = gni_per_capita

        # Dose tracking
        self.dose1_total = 0
        self.dose2_total = 0

        # Queues: (day_administered, count_per_age_group)
        self.dose1_queue: deque = deque()  # People waiting for dose 2
        self.dose2_queue: deque = deque()  # People building full immunity after dose 2

        # Immunity tracking per age group
        self.partial_immune = np.zeros(NUM_AGE_GROUPS, dtype=int)
        self.fully_immune = np.zeros(NUM_AGE_GROUPS, dtype=int)

        # Age-priority vaccination order (oldest first)
        self.age_priority = [4, 3, 2, 1, 0]  # 80+, 65-79, 45-64, 18-44, 0-17

        # Hesitancy
        self._acceptance_rate = self._compute_acceptance_rate()

    def _compute_acceptance_rate(self) -> float:
        """Compute country-specific vaccine acceptance rate based on GNI."""
        return min(0.95, 0.4 + 0.3 * np.log(self.gni_per_capita / 1000 + 1))

    @property
    def acceptance_rate(self) -> float:
        return self._acceptance_rate

    def max_daily_vaccines(self) -> int:
        """Maximum vaccines this country can administer per day."""
        base_rate = self.population * self.params.max_daily_fraction
        # Infrastructure factor based on GNI
        infra = np.log(self.gni_per_capita / 1000 + 1) / np.log(100)
        infra = max(0.1, min(1.0, infra))
        return max(1, int(base_rate * infra))

    def administer_dose1(self, day: int, vaccines: int, susceptible_by_age: np.ndarray) -> np.ndarray:
        """
        Administer first doses, prioritizing oldest age groups.

        Args:
            day: Current simulation day
            vaccines: Number of vaccines available for dose 1
            susceptible_by_age: Susceptible population per age group

        Returns:
            Array of vaccines administered per age group
        """
        effective_vaccines = int(vaccines * self._acceptance_rate)
        administered = np.zeros(NUM_AGE_GROUPS, dtype=int)
        remaining = effective_vaccines

        for age_idx in self.age_priority:
            if remaining <= 0:
                break
            available = int(susceptible_by_age[age_idx])
            give = min(available, remaining)
            administered[age_idx] = give
            remaining -= give

        total = int(administered.sum())
        if total > 0:
            self.dose1_total += total
            self.dose1_queue.append((day, administered.copy()))

        return administered

    def process_day(self, day: int, compartments) -> Dict[str, int]:
        """
        Process vaccination events for the current day:
        1. Check if any dose1 recipients are due for dose2
        2. Check if any dose2 recipients have reached full immunity
        3. Check if any dose1 recipients have reached partial immunity

        Returns dict with counts of new partial and full immunity gained.
        """
        new_partial = 0
        new_full = 0
        dose2_needed = 0

        # Process dose 1 queue: after immunity_delay_dose1 days, gain partial immunity
        # After dose_interval days, they need dose 2
        items_to_remove = []
        for i, (admin_day, counts) in enumerate(self.dose1_queue):
            days_since = day - admin_day

            # Partial immunity kicks in
            if days_since == self.params.immunity_delay_dose1:
                new_partial += int(counts.sum())

            # Due for dose 2
            if days_since >= self.params.dose_interval:
                items_to_remove.append(i)
                # Administer dose 2 automatically (from same vaccine supply conceptually)
                self.dose2_total += int(counts.sum())
                self.dose2_queue.append((day, counts.copy()))
                dose2_needed += int(counts.sum())

        # Remove processed items (in reverse to maintain indices)
        for i in reversed(items_to_remove):
            del self.dose1_queue[i]

        # Process dose 2 queue: after immunity_delay_dose2, gain full immunity
        items_to_remove = []
        for i, (admin_day, counts) in enumerate(self.dose2_queue):
            if day - admin_day >= self.params.immunity_delay_dose2:
                items_to_remove.append(i)
                # Move to V compartment
                compartments.V += counts
                compartments.S = np.maximum(0, compartments.S - counts)
                new_full += int(counts.sum())
                self.fully_immune += counts

        for i in reversed(items_to_remove):
            del self.dose2_queue[i]

        return {
            'new_partial_immune': new_partial,
            'new_fully_immune': new_full,
            'dose2_administered': dose2_needed,
        }
