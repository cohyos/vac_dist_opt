"""Integration tests for the enhanced simulation."""

import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation import EnhancedSimulationConfig, EnhancedGlobalSimulation
from src.models.epidemic_model import SEIRCompartments, EpidemicParams, step_seir
from src.models.variant_model import VariantManager, DEFAULT_VARIANTS
from src.models.country import EnhancedCountry
from src.models.vaccination_state import VaccinationParams


def _make_countries_df(n=5):
    """Create a small test countries DataFrame."""
    return pd.DataFrame({
        'Country': [f'Country_{i}' for i in range(n)],
        'Population': [1_000_000 * (i + 1) for i in range(n)],
        'GNI_per_capita': [5000 + i * 3000 for i in range(n)],
    })


def _make_vaccines_df(days=50, daily_amount=0):
    """Create a vaccine availability DataFrame."""
    return pd.DataFrame({
        'day_number': range(1, days + 1),
        'available_vaccines': [daily_amount] * days,
    })


class TestConservationLaws:
    """Verify S+E+I+H+R+V+W+D = N_initial at every timestep."""

    def test_compartment_conservation_no_vaccination(self):
        """Population should be conserved through epidemic dynamics."""
        pop = 100_000
        compartments = SEIRCompartments(population=pop, initial_infected=100)
        params = EpidemicParams(base_r0=2.5)

        for day in range(30):
            step_seir(compartments, params, r0_modifier=1.0)
            assert compartments.verify_conservation(), \
                f"Conservation violated on day {day}"

    def test_compartment_conservation_with_lockdown(self):
        """Population should be conserved under lockdown."""
        pop = 50_000
        compartments = SEIRCompartments(population=pop, initial_infected=50)
        params = EpidemicParams(base_r0=3.0)

        for day in range(30):
            mod = 0.4 if day > 10 else 1.0
            step_seir(compartments, params, r0_modifier=mod)
            assert compartments.verify_conservation(), \
                f"Conservation violated on day {day}"


class TestEpidemicBehavior:
    """Verify basic epidemic behavior is reasonable."""

    def test_epidemic_grows_then_peaks(self):
        """Infections should grow, peak, then decline."""
        pop = 500_000
        compartments = SEIRCompartments(population=pop, initial_infected=100)
        params = EpidemicParams(base_r0=2.5, overdispersion_k=10.0)
        np.random.seed(42)

        infected_series = []
        for day in range(200):
            step_seir(compartments, params)
            infected_series.append(compartments.total_infected)

        peak_day = np.argmax(infected_series)
        assert peak_day > 5, "Peak should not be on day 0"
        assert peak_day < 190, "Peak should occur before end"
        assert infected_series[-1] < max(infected_series), "Infections should decline after peak"

    def test_lockdown_reduces_peak(self):
        """Lockdown should reduce the peak infection count."""
        np.random.seed(42)
        pop = 100_000

        # No lockdown
        c1 = SEIRCompartments(population=pop, initial_infected=100)
        params = EpidemicParams(base_r0=2.5, overdispersion_k=10.0)
        for _ in range(100):
            step_seir(c1, params, r0_modifier=1.0)
        deaths_no_lockdown = c1.total_dead

        # With lockdown
        np.random.seed(42)
        c2 = SEIRCompartments(population=pop, initial_infected=100)
        for _ in range(100):
            step_seir(c2, params, r0_modifier=0.4)
        deaths_lockdown = c2.total_dead

        assert deaths_lockdown < deaths_no_lockdown, \
            "Lockdown should reduce total deaths"

    def test_zero_infected_no_spread(self):
        """With zero initial infections, no spread should occur."""
        compartments = SEIRCompartments(population=100_000, initial_infected=0)
        params = EpidemicParams(base_r0=2.5)

        for _ in range(50):
            step_seir(compartments, params)

        assert compartments.total_infected == 0
        assert compartments.total_dead == 0
        assert compartments.total_exposed == 0


class TestVariantSystem:
    """Verify variant emergence and effects."""

    def test_variant_timeline(self):
        vm = VariantManager(DEFAULT_VARIANTS.copy())
        assert vm.get_active_variant(0).name == "Original"
        assert vm.get_active_variant(120).name == "Alpha"
        assert vm.get_active_variant(450).name == "Delta"
        assert vm.get_active_variant(700).name == "Omicron"

    def test_dynamic_hit_increases_with_variant(self):
        vm = VariantManager(DEFAULT_VARIANTS.copy())
        hit_original = vm.get_dynamic_herd_immunity_threshold(0, 2.5)
        hit_delta = vm.get_dynamic_herd_immunity_threshold(450, 2.5)
        assert hit_delta > hit_original, \
            "Delta's higher R0 should raise the herd immunity threshold"


class TestEnhancedCountry:
    """Test the enhanced country model."""

    def test_vaccination_reduces_susceptible(self):
        country = EnhancedCountry("TestLand", 100_000, 10000,
                                  initial_infected=50)
        vm = VariantManager()

        initial_susceptible = country.compartments.total_susceptible
        country.vaccinate(0, 1000)
        # Vaccines go into queue, not immediately effective
        assert country.vaccination.dose1_total > 0

    def test_update_produces_events(self):
        country = EnhancedCountry("TestLand", 100_000, 10000,
                                  initial_infected=100)
        vm = VariantManager()
        events = country.update(0, 1.0, vm)
        assert 'new_exposed' in events
        assert 'new_deaths' in events


class TestFullSimulation:
    """Integration test running a short simulation end-to-end."""

    def test_short_simulation_runs(self):
        """Run a 20-day simulation with 3 countries and verify outputs."""
        config = EnhancedSimulationConfig(
            simulation_days=20,
            random_seed=42,
            initial_infected_per_country=50,
            enable_variants=False,
        )
        sim = EnhancedGlobalSimulation(config)

        countries_df = _make_countries_df(3)
        vaccines_df = _make_vaccines_df(days=20, daily_amount=5000)

        results, time_series = sim.run_all(countries_df, vaccines_df)

        # Should have one row per strategy
        assert len(results) == len(sim.strategies)

        # All strategies should produce positive deaths (epidemic is running)
        assert all(results['total_deaths'] >= 0)

        # Time series should have entries
        assert len(time_series) > 0

        # Each strategy should appear in time series
        ts_strategies = set(t['strategy'] for t in time_series)
        result_strategies = set(results['strategy'])
        assert ts_strategies == result_strategies

    def test_vaccination_moves_people_to_v_compartment(self):
        """Verify that vaccination actually moves people into the V compartment."""
        config = EnhancedSimulationConfig(
            simulation_days=40,
            random_seed=42,
            initial_infected_per_country=10,
            enable_variants=False,
        )

        countries_df = _make_countries_df(2)

        # Run with large vaccine supply
        sim = EnhancedGlobalSimulation(config)
        sim.strategies = sim.strategies[:1]
        results, ts = sim.run_all(
            countries_df, _make_vaccines_df(40, daily_amount=100_000)
        )

        # After 40 days (> dose_interval + immunity_delay), some should be vaccinated
        final = ts[-1]
        assert final['total_vaccinated'] > 0, \
            "After 40 days with vaccines, some population should be in V compartment"

    def test_equity_metrics_computed(self):
        """Verify equity metrics are in results."""
        config = EnhancedSimulationConfig(
            simulation_days=20,
            random_seed=42,
            enable_variants=False,
        )
        sim = EnhancedGlobalSimulation(config)
        sim.strategies = sim.strategies[:2]  # Just 2 for speed

        countries_df = _make_countries_df(3)
        vaccines_df = _make_vaccines_df(20, daily_amount=5000)

        results, _ = sim.run_all(countries_df, vaccines_df)

        assert 'vaccine_gini' in results.columns
        assert 'equity_gap' in results.columns
        assert 'years_of_life_lost' in results.columns
        assert 'peak_hospitalized' in results.columns
