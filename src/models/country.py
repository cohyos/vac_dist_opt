"""
Enhanced Country model integrating SEIR+ epidemic model,
vaccination state, and variant tracking.
"""

import numpy as np
from typing import Dict, Optional
from src.models.epidemic_model import (
    SEIRCompartments, EpidemicParams, step_seir, NUM_AGE_GROUPS
)
from src.models.vaccination_state import VaccinationState, VaccinationParams
from src.models.variant_model import VariantManager


class EnhancedCountry:
    """A country with SEIR+ epidemic dynamics, vaccination, and variant tracking."""

    def __init__(self, name: str, population: int, gni_per_capita: float,
                 epidemic_params: EpidemicParams = None,
                 vaccination_params: VaccinationParams = None,
                 age_distribution: np.ndarray = None,
                 initial_infected: int = 100):
        self.name = name
        self.population = population
        self.gni_per_capita = gni_per_capita
        self.gni = population * gni_per_capita  # National GNI

        # Initialize epidemic compartments
        self.epidemic_params = epidemic_params or EpidemicParams()
        self.compartments = SEIRCompartments(
            population=population,
            age_distribution=age_distribution,
            initial_infected=initial_infected
        )

        # Initialize vaccination state
        self.vaccination = VaccinationState(
            population=population,
            gni_per_capita=gni_per_capita,
            params=vaccination_params
        )

        # Immunity tracking
        self.has_reached_immunity = False
        self.day_reached_immunity = None

    def get_immunity_percentage(self) -> float:
        """Current immunity percentage (recovered + vaccinated)."""
        return self.compartments.get_immunity_percentage()

    def max_daily_vaccines(self) -> int:
        """Maximum vaccines this country can absorb per day."""
        return self.vaccination.max_daily_vaccines()

    def vaccinate(self, day: int, num_vaccines: int) -> np.ndarray:
        """Administer vaccines, returning per-age-group counts."""
        return self.vaccination.administer_dose1(
            day, num_vaccines, self.compartments.S
        )

    def update(self, day: int, npi_r0_modifier: float,
               variant_manager: VariantManager) -> Dict:
        """
        Advance one day: variant effects, vaccination processing, epidemic step.

        Args:
            day: Current simulation day
            npi_r0_modifier: R0 multiplier from NPIs/lockdowns (0-1)
            variant_manager: Manages variant emergence and effects

        Returns:
            Dict with daily event counts
        """
        # Apply variant immune escape (on emergence day)
        lost_immunity = variant_manager.apply_immune_escape(day, self.compartments)

        # Process vaccination queue (dose scheduling, immunity delays)
        vax_events = self.vaccination.process_day(day, self.compartments)

        # Combined R0 modifier: NPI × variant
        variant_r0 = variant_manager.get_r0_modifier(day)
        combined_r0_modifier = npi_r0_modifier * variant_r0

        # Variant-adjusted vaccine efficacy
        vax_efficacy = (self.vaccination.params.efficacy_dose2 *
                       variant_manager.get_vaccine_efficacy_modifier(day))

        # Step epidemic model
        epi_events = step_seir(
            self.compartments,
            self.epidemic_params,
            r0_modifier=combined_r0_modifier,
            vaccine_efficacy=vax_efficacy
        )

        # Dynamic herd immunity threshold
        hit = variant_manager.get_dynamic_herd_immunity_threshold(
            day, self.epidemic_params.base_r0
        )
        immunity_reached = False
        if not self.has_reached_immunity and self.get_immunity_percentage() >= hit * 100:
            self.has_reached_immunity = True
            self.day_reached_immunity = day
            immunity_reached = True

        return {
            **epi_events,
            **vax_events,
            'lost_immunity': lost_immunity,
            'reached_immunity': immunity_reached,
            'herd_immunity_threshold': hit * 100,
        }
