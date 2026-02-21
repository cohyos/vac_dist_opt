"""
Enhanced global simulation orchestrator.

Integrates SEIR+ epidemic model, variant tracking, per-country NPIs,
dose-scheduled vaccination, and equity metrics.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from src.models.country import EnhancedCountry
from src.models.epidemic_model import EpidemicParams
from src.models.variant_model import VariantManager, DEFAULT_VARIANTS
from src.models.vaccination_state import VaccinationParams
from src.interventions.lockdown_controller import GlobalNPIManager
from src.strategies.base_strategy import AllocationStrategy
from src.strategies.proportional import (
    PopulationProportional, large_population_first, small_population_first,
    high_gdp_first, low_gdp_first, high_gni_first, low_gni_first
)
from src.strategies.needs_based import InfectionRateBased, COVAXLike, MortalityRiskBased
from src.analysis.equity_metrics import vaccine_gini, equity_gap, years_of_life_lost


class EnhancedSimulationConfig:
    """Configuration for the enhanced simulation."""

    def __init__(self, **kwargs):
        # Simulation parameters
        self.simulation_days: int = kwargs.get('simulation_days', 800)
        self.random_seed: Optional[int] = kwargs.get('random_seed', 42)
        self.initial_infected_per_country: int = kwargs.get('initial_infected_per_country', 100)

        # Epidemic parameters
        self.epidemic_params = EpidemicParams(
            base_r0=kwargs.get('basic_reproduction_number', 2.5),
            overdispersion_k=kwargs.get('overdispersion_k', 0.1),
            incubation_period=kwargs.get('incubation_period', 5.2),
            infectious_period=kwargs.get('infectious_period', 10.0),
            hospital_stay=kwargs.get('hospital_stay', 10.0),
            hospital_beds_per_capita=kwargs.get('hospital_beds_per_capita', 0.003),
            mortality_multiplier_over_capacity=kwargs.get('mortality_multiplier_over_capacity', 2.0),
            natural_immunity_half_life=kwargs.get('natural_immunity_half_life', 180.0),
            vaccine_immunity_half_life=kwargs.get('vaccine_immunity_half_life', 150.0),
        )

        # Vaccination parameters
        self.vaccination_params = VaccinationParams(
            dose_interval=kwargs.get('dose_interval', 21),
            immunity_delay_dose1=kwargs.get('immunity_delay_dose1', 14),
            immunity_delay_dose2=kwargs.get('immunity_delay_dose2', 7),
            efficacy_dose1=kwargs.get('efficacy_dose1', 0.52),
            efficacy_dose2=kwargs.get('efficacy_dose2', 0.95),
            max_daily_fraction=kwargs.get('max_daily_fraction', 0.005),
        )

        # Variant configuration
        self.enable_variants: bool = kwargs.get('enable_variants', True)

        # Thresholds for analysis
        self.herd_immunity_threshold: float = kwargs.get('herd_immunity_threshold', 0.7)
        self.country_immunity_threshold: float = kwargs.get('country_immunity_threshold', 0.5)

    @classmethod
    def from_yaml(cls, path: str) -> 'EnhancedSimulationConfig':
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class EnhancedGlobalSimulation:
    """Enhanced simulation with SEIR+, variants, per-country NPIs, and equity metrics."""

    def __init__(self, config: EnhancedSimulationConfig):
        self.config = config
        self.variant_manager = VariantManager(
            DEFAULT_VARIANTS if config.enable_variants else None
        )

        # Build strategy list
        self.strategies: List[AllocationStrategy] = [
            PopulationProportional(),
            large_population_first(),
            small_population_first(),
            high_gdp_first(),
            low_gdp_first(),
            high_gni_first(),
            low_gni_first(),
            InfectionRateBased(),
            COVAXLike(floor_coverage=0.20),
            MortalityRiskBased(),
        ]

        # Per-strategy results
        self.npi_managers: Dict[str, GlobalNPIManager] = {}

    def _init_countries(self, countries_data: pd.DataFrame) -> Dict[str, EnhancedCountry]:
        """Initialize countries from DataFrame."""
        countries = {}
        for _, row in countries_data.iterrows():
            name = row['Country']
            countries[name] = EnhancedCountry(
                name=name,
                population=int(row['Population']),
                gni_per_capita=float(row['GNI_per_capita']),
                epidemic_params=self.config.epidemic_params,
                vaccination_params=self.config.vaccination_params,
                initial_infected=self.config.initial_infected_per_country,
            )
        return countries

    def _run_single_strategy(self, countries_data: pd.DataFrame,
                              vaccines_data: pd.DataFrame,
                              strategy: AllocationStrategy) -> Tuple[Dict, List[Dict]]:
        """Run simulation for a single strategy."""
        countries = self._init_countries(countries_data)
        num_countries = len(countries)

        # Initialize per-country NPI manager
        npi_manager = GlobalNPIManager()
        for name in countries:
            npi_manager.add_country(name)

        # Reset variant manager state
        variant_mgr = VariantManager(
            DEFAULT_VARIANTS.copy() if self.config.enable_variants else None
        )

        time_series = []
        simulation_days = min(self.config.simulation_days, len(vaccines_data))

        for day in tqdm(range(simulation_days), desc=strategy.name, leave=False):
            # Get available vaccines
            available_vaccines = max(0, int(vaccines_data.iloc[day]['available_vaccines']))

            # Allocate vaccines
            allocations = strategy.allocate(countries, available_vaccines)

            # Administer vaccines
            for name, num_vax in allocations.items():
                if num_vax > 0:
                    countries[name].vaccinate(day, num_vax)

            # Compute per-country infection rates for NPI decisions
            infection_rates = {}
            for name, country in countries.items():
                pop = country.compartments.total_population
                inf = country.compartments.total_infected
                infection_rates[name] = inf / pop if pop > 0 else 0

            # Update per-country NPIs
            r0_modifiers = npi_manager.update_all(day, infection_rates)

            # Update epidemic in each country
            for name, country in countries.items():
                npi_mod = r0_modifiers.get(name, 1.0)
                country.update(day, npi_mod, variant_mgr)

            # Collect statistics
            stats = self._collect_stats(countries, day, strategy.name, variant_mgr)
            time_series.append(stats)

        # Store NPI manager for this strategy
        self.npi_managers[strategy.name] = npi_manager

        # Analyze results
        final_stats = self._analyze_results(time_series, strategy.name, num_countries)
        final_stats['vaccine_gini'] = vaccine_gini(countries)
        final_stats['equity_gap'] = equity_gap(countries)
        final_stats['years_of_life_lost'] = years_of_life_lost(countries)

        return final_stats, time_series

    def _collect_stats(self, countries: Dict[str, EnhancedCountry], day: int,
                       strategy: str, variant_mgr: VariantManager) -> Dict:
        """Collect global statistics for one timestep."""
        total_pop = max(1, sum(c.compartments.total_population for c in countries.values()))
        total_gni = max(1, sum(c.gni for c in countries.values()))

        total_infected = sum(c.compartments.total_infected for c in countries.values())
        total_exposed = sum(c.compartments.total_exposed for c in countries.values())
        total_hospitalized = sum(c.compartments.total_hospitalized for c in countries.values())
        total_deaths = sum(c.compartments.total_dead for c in countries.values())
        total_vaccinated = sum(c.compartments.total_vaccinated for c in countries.values())

        # Population-weighted immunity
        global_immunity = sum(
            c.get_immunity_percentage() * c.population for c in countries.values()
        ) / total_pop

        # GNI-weighted immunity
        economic_immunity = sum(
            c.get_immunity_percentage() * c.gni for c in countries.values()
        ) / total_gni

        # Dynamic HIT
        hit = variant_mgr.get_dynamic_herd_immunity_threshold(
            day, self.config.epidemic_params.base_r0
        ) * 100

        countries_with_immunity = sum(
            1 for c in countries.values()
            if c.get_immunity_percentage() >= hit
        )

        return {
            'day': day,
            'strategy': strategy,
            'global_immunity_percentage': global_immunity,
            'economic_immunity_percentage': economic_immunity,
            'countries_with_immunity': countries_with_immunity,
            'total_deaths': total_deaths,
            'total_infected': total_infected,
            'total_exposed': total_exposed,
            'total_hospitalized': total_hospitalized,
            'total_vaccinated': total_vaccinated,
            'infection_rate': (total_infected / total_pop) * 100,
            'variant': variant_mgr.get_active_variant(day).name,
            'herd_immunity_threshold': hit,
        }

    def _analyze_results(self, time_series: List[Dict], strategy: str,
                         num_countries: int) -> Dict:
        """Analyze strategy results."""
        df = pd.DataFrame(time_series)

        # Use dynamic HIT from last day for threshold
        final_hit = df.iloc[-1]['herd_immunity_threshold'] if len(df) > 0 else 70.0
        country_threshold = self.config.country_immunity_threshold * num_countries

        days_to_global = None
        if (df['global_immunity_percentage'] >= final_hit).any():
            days_to_global = int(df[df['global_immunity_percentage'] >= final_hit].iloc[0]['day'])

        days_to_economic = None
        if (df['economic_immunity_percentage'] >= final_hit).any():
            days_to_economic = int(df[df['economic_immunity_percentage'] >= final_hit].iloc[0]['day'])

        days_to_countries = None
        if (df['countries_with_immunity'] >= country_threshold).any():
            days_to_countries = int(df[df['countries_with_immunity'] >= country_threshold].iloc[0]['day'])

        peak_hospitalized = int(df['total_hospitalized'].max()) if 'total_hospitalized' in df else 0

        return {
            'strategy': strategy,
            'days_to_70_global': days_to_global,
            'days_to_70_economic': days_to_economic,
            'days_to_50_countries': days_to_countries,
            'total_deaths': int(df.iloc[-1]['total_deaths']),
            'peak_hospitalized': peak_hospitalized,
        }

    def run_all(self, countries_data: pd.DataFrame,
                vaccines_data: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Run simulation for all strategies."""
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

        results = []
        all_time_series = []

        for strategy in self.strategies:
            print(f"\nRunning {strategy.name}...")
            try:
                result, ts = self._run_single_strategy(countries_data, vaccines_data, strategy)
                results.append(result)
                all_time_series.extend(ts)
                print(f"  Deaths: {result['total_deaths']:,} | "
                      f"Gini: {result.get('vaccine_gini', 0):.3f} | "
                      f"YLL: {result.get('years_of_life_lost', 0):,.0f}")
            except Exception as e:
                print(f"  Error: {e}")
                continue

        return pd.DataFrame(results), all_time_series
