"""Tests for vaccination state and dose scheduling."""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.epidemic_model import SEIRCompartments, NUM_AGE_GROUPS
from src.models.vaccination_state import VaccinationState, VaccinationParams


class TestVaccinationState:
    def setup_method(self):
        self.vax_state = VaccinationState(
            population=1_000_000,
            gni_per_capita=10000,
            params=VaccinationParams(
                dose_interval=21,
                immunity_delay_dose1=14,
                immunity_delay_dose2=7,
            )
        )

    def test_acceptance_rate_positive(self):
        assert 0 < self.vax_state.acceptance_rate <= 1.0

    def test_max_daily_positive(self):
        assert self.vax_state.max_daily_vaccines() > 0

    def test_administer_dose1(self):
        susceptible = np.ones(NUM_AGE_GROUPS, dtype=int) * 100_000
        administered = self.vax_state.administer_dose1(0, 5_000, susceptible)
        assert administered.sum() > 0
        assert administered.sum() <= 5_000
        assert self.vax_state.dose1_total > 0

    def test_age_priority_oldest_first(self):
        """Oldest age groups should be vaccinated first."""
        susceptible = np.ones(NUM_AGE_GROUPS, dtype=int) * 100_000
        # Give very few vaccines so only highest priority groups get them
        administered = self.vax_state.administer_dose1(0, 100, susceptible)
        # Age group 4 (80+) should get vaccines first
        assert administered[4] > 0

    def test_dose2_scheduling(self):
        """After dose_interval days, dose 2 should be administered."""
        compartments = SEIRCompartments(population=1_000_000, initial_infected=0)
        susceptible = compartments.S.copy()
        self.vax_state.administer_dose1(0, 1000, susceptible)

        # Fast forward to dose_interval
        for day in range(1, 22):
            result = self.vax_state.process_day(day, compartments)

        # By day 21, dose 2 should have been administered
        assert self.vax_state.dose2_total > 0

    def test_full_immunity_delayed(self):
        """Full immunity should come after dose2 + immunity_delay_dose2."""
        compartments = SEIRCompartments(population=1_000_000, initial_infected=0)
        susceptible = compartments.S.copy()
        self.vax_state.administer_dose1(0, 1000, susceptible)

        # Process until full immunity should kick in (day 21 + 7 = 28)
        for day in range(1, 30):
            result = self.vax_state.process_day(day, compartments)

        assert compartments.total_vaccinated > 0


class TestVaccinationParams:
    def test_defaults(self):
        p = VaccinationParams()
        assert p.dose_interval == 21
        assert p.efficacy_dose1 < p.efficacy_dose2

    def test_hesitancy_varies_by_gni(self):
        rich = VaccinationState(population=100_000, gni_per_capita=50000)
        poor = VaccinationState(population=100_000, gni_per_capita=500)
        assert rich.acceptance_rate > poor.acceptance_rate
