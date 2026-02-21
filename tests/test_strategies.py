"""Tests for vaccine allocation strategies."""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.country import EnhancedCountry
from src.models.epidemic_model import EpidemicParams
from src.strategies.proportional import (
    PopulationProportional, large_population_first, small_population_first,
    high_gni_first, low_gni_first
)
from src.strategies.needs_based import InfectionRateBased, COVAXLike, MortalityRiskBased


def make_countries(specs):
    """Helper: create test countries from (name, pop, gni) tuples."""
    countries = {}
    for name, pop, gni in specs:
        countries[name] = EnhancedCountry(
            name=name, population=pop, gni_per_capita=gni,
            epidemic_params=EpidemicParams(), initial_infected=10
        )
    return countries


class TestPopulationProportional:
    def test_proportional_allocation(self):
        countries = make_countries([
            ('A', 1_000_000, 10000),
            ('B', 500_000, 10000),
        ])
        strategy = PopulationProportional()
        alloc = strategy.allocate(countries, 100_000)
        # A should get roughly 2x B
        assert alloc['A'] > alloc['B']
        assert alloc['A'] + alloc['B'] <= 100_000

    def test_zero_vaccines(self):
        countries = make_countries([('A', 100_000, 10000)])
        strategy = PopulationProportional()
        alloc = strategy.allocate(countries, 0)
        assert alloc['A'] == 0

    def test_empty_countries(self):
        strategy = PopulationProportional()
        alloc = strategy.allocate({}, 100_000)
        assert alloc == {}


class TestPriorityStrategies:
    def test_large_pop_prioritizes_big_countries(self):
        countries = make_countries([
            ('Big', 10_000_000, 5000),
            ('Small', 100_000, 5000),
        ])
        strategy = large_population_first()
        alloc = strategy.allocate(countries, 50_000)
        assert alloc['Big'] > alloc['Small']

    def test_high_gni_prioritizes_rich_countries(self):
        countries = make_countries([
            ('Rich', 1_000_000, 50000),
            ('Poor', 1_000_000, 1000),
        ])
        strategy = high_gni_first()
        alloc = strategy.allocate(countries, 50_000)
        assert alloc['Rich'] > alloc['Poor']


class TestCOVAXLike:
    def test_floor_allocation(self):
        countries = make_countries([
            ('A', 100_000, 50000),
            ('B', 100_000, 1000),
        ])
        strategy = COVAXLike(floor_coverage=0.20)
        alloc = strategy.allocate(countries, 50_000)
        # Both should get vaccines (floor ensures equity)
        assert alloc['A'] > 0
        assert alloc['B'] > 0

    def test_total_does_not_exceed_available(self):
        countries = make_countries([
            ('A', 1_000_000, 10000),
            ('B', 1_000_000, 10000),
        ])
        strategy = COVAXLike()
        alloc = strategy.allocate(countries, 5_000)
        assert sum(alloc.values()) <= 5_000


class TestInfectionRateBased:
    def test_prioritizes_high_infection_countries(self):
        countries = make_countries([
            ('High', 100_000, 10000),
            ('Low', 100_000, 10000),
        ])
        # Manually increase infections in 'High'
        countries['High'].compartments.I[:] = 1000
        countries['Low'].compartments.I[:] = 10

        strategy = InfectionRateBased()
        alloc = strategy.allocate(countries, 10_000)
        assert alloc['High'] > alloc['Low']
