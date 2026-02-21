"""Tests for the SEIR+ epidemic model."""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.epidemic_model import (
    SEIRCompartments, EpidemicParams, step_seir,
    NUM_AGE_GROUPS, DEFAULT_AGE_DISTRIBUTION
)


class TestSEIRCompartments:
    def test_initialization(self):
        c = SEIRCompartments(population=1_000_000, initial_infected=100)
        assert c.total_susceptible + c.total_infected == 1_000_000
        assert c.total_infected == 100
        assert c.total_exposed == 0
        assert c.total_hospitalized == 0
        assert c.total_recovered == 0
        assert c.total_dead == 0

    def test_conservation_initial(self):
        c = SEIRCompartments(population=1_000_000, initial_infected=100)
        assert c.verify_conservation()

    def test_conservation_after_steps(self):
        np.random.seed(42)
        c = SEIRCompartments(population=100_000, initial_infected=50)
        p = EpidemicParams(base_r0=2.5)
        for _ in range(50):
            step_seir(c, p)
        assert c.verify_conservation(), "Conservation law violated after 50 steps"

    def test_no_infections_with_zero_infected(self):
        np.random.seed(42)
        c = SEIRCompartments(population=100_000, initial_infected=0)
        p = EpidemicParams(base_r0=2.5)
        events = step_seir(c, p)
        assert events['new_exposed'] == 0
        assert c.total_susceptible == 100_000

    def test_epidemic_grows_with_high_r0(self):
        np.random.seed(42)
        c = SEIRCompartments(population=100_000, initial_infected=100)
        p = EpidemicParams(base_r0=3.0)
        initial_infected = c.total_infected
        for _ in range(20):
            step_seir(c, p)
        # After 20 days with R0=3, infections should have grown significantly
        total_ever_infected = c.total_infected + c.total_exposed + c.total_recovered + c.total_hospitalized + c.total_dead
        assert total_ever_infected > initial_infected * 5

    def test_lockdown_reduces_infections(self):
        np.random.seed(42)
        # Run without lockdown
        c1 = SEIRCompartments(population=100_000, initial_infected=100)
        p = EpidemicParams(base_r0=2.5)
        for _ in range(30):
            step_seir(c1, p, r0_modifier=1.0)
        deaths_no_lockdown = c1.total_dead

        # Run with lockdown (0.4x R0)
        np.random.seed(42)
        c2 = SEIRCompartments(population=100_000, initial_infected=100)
        for _ in range(30):
            step_seir(c2, p, r0_modifier=0.4)
        deaths_lockdown = c2.total_dead

        assert deaths_lockdown < deaths_no_lockdown

    def test_age_groups_sum_to_population(self):
        c = SEIRCompartments(population=1_000_000, initial_infected=100)
        assert c.N.sum() == 1_000_000


class TestEpidemicParams:
    def test_default_params(self):
        p = EpidemicParams()
        assert p.base_r0 == 2.5
        assert p.incubation_period == 5.2
        assert p.infectious_period == 10.0
        assert len(p.ifr_by_age) == NUM_AGE_GROUPS

    def test_ifr_increases_with_age(self):
        p = EpidemicParams()
        for i in range(len(p.ifr_by_age) - 1):
            assert p.ifr_by_age[i] < p.ifr_by_age[i + 1], \
                f"IFR should increase with age: {p.ifr_by_age}"
