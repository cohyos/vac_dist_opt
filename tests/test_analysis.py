"""Tests for equity metrics and analysis."""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.equity_metrics import gini_coefficient, years_of_life_lost, LIFE_EXPECTANCY_BY_AGE
from src.models.country import EnhancedCountry
from src.models.epidemic_model import EpidemicParams


class TestGiniCoefficient:
    def test_perfect_equality(self):
        values = np.array([10, 10, 10, 10])
        assert gini_coefficient(values) == pytest.approx(0.0, abs=0.01)

    def test_maximum_inequality(self):
        values = np.array([0, 0, 0, 100])
        assert gini_coefficient(values) > 0.5

    def test_empty_array(self):
        assert gini_coefficient(np.array([])) == 0.0

    def test_all_zeros(self):
        assert gini_coefficient(np.array([0, 0, 0])) == 0.0

    def test_intermediate_inequality(self):
        values = np.array([1, 2, 3, 4, 5])
        g = gini_coefficient(values)
        assert 0 < g < 1


class TestYearsOfLifeLost:
    def test_no_deaths_zero_yll(self):
        country = EnhancedCountry('Test', 100_000, 10000,
                                   epidemic_params=EpidemicParams(),
                                   initial_infected=0)
        yll = years_of_life_lost({'test': country})
        assert yll == 0.0

    def test_elderly_deaths_less_yll_per_death(self):
        """Deaths in older age groups should produce fewer YLL per death."""
        # The LIFE_EXPECTANCY_BY_AGE should decrease with age
        for i in range(len(LIFE_EXPECTANCY_BY_AGE) - 1):
            assert LIFE_EXPECTANCY_BY_AGE[i] > LIFE_EXPECTANCY_BY_AGE[i + 1]
