"""
Variant model for COVID-19 simulation.

Models the emergence of new variants over time, each with different
transmissibility, immune escape, severity, and vaccine efficacy.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass
class Variant:
    """Represents a viral variant with its epidemiological properties."""
    name: str
    r0_multiplier: float         # Relative to base R0 (Original = 1.0)
    immune_escape: float         # Fraction of immune who become re-susceptible (0-1)
    severity_multiplier: float   # Relative severity vs Original (affects IFR/hosp)
    vaccine_efficacy_multiplier: float  # Relative vaccine efficacy (1.0 = no reduction)
    emergence_day: int           # Day when this variant appears


# Default variant timeline based on real-world COVID-19 evolution
DEFAULT_VARIANTS = [
    Variant("Original", 1.0, 0.0, 1.0, 1.0, 0),
    Variant("Alpha", 1.5, 0.0, 1.1, 0.95, 120),     # ~Apr 2020
    Variant("Delta", 2.4, 0.15, 1.5, 0.80, 450),     # ~Mar 2021
    Variant("Omicron", 4.0, 0.40, 0.6, 0.55, 700),   # ~Dec 2021
]


class VariantManager:
    """Manages variant emergence and computes effective parameters."""

    def __init__(self, variants: List[Variant] = None):
        self.variants = variants if variants is not None else DEFAULT_VARIANTS.copy()
        self.variants.sort(key=lambda v: v.emergence_day)
        self.current_variant_idx = 0

    def get_active_variant(self, day: int) -> Variant:
        """Get the dominant variant for a given simulation day."""
        active = self.variants[0]
        for v in self.variants:
            if day >= v.emergence_day:
                active = v
        return active

    def get_r0_modifier(self, day: int) -> float:
        """Get the R0 multiplier for the current day's dominant variant."""
        return self.get_active_variant(day).r0_multiplier

    def get_severity_modifier(self, day: int) -> float:
        """Get severity multiplier for the current day's dominant variant."""
        return self.get_active_variant(day).severity_multiplier

    def get_vaccine_efficacy_modifier(self, day: int) -> float:
        """Get vaccine efficacy multiplier for the current variant."""
        return self.get_active_variant(day).vaccine_efficacy_multiplier

    def get_immune_escape(self, day: int) -> float:
        """Get immune escape fraction for the current variant."""
        return self.get_active_variant(day).immune_escape

    def apply_immune_escape(self, day: int, compartments) -> int:
        """
        When a new variant with immune escape emerges, move a fraction
        of recovered/vaccinated back to waned/susceptible.

        Returns number of people who lost immunity.
        """
        variant = self.get_active_variant(day)
        escape = variant.immune_escape

        if escape <= 0:
            return 0

        # Check if this variant just emerged (within transition window)
        if day != variant.emergence_day:
            return 0

        # Move fraction of R and V to W (waned)
        lost_R = (compartments.R * escape).astype(int)
        lost_V = (compartments.V * escape).astype(int)

        compartments.R = np.maximum(0, compartments.R - lost_R)
        compartments.V = np.maximum(0, compartments.V - lost_V)
        compartments.W += lost_R + lost_V

        return int(lost_R.sum() + lost_V.sum())

    def get_dynamic_herd_immunity_threshold(self, day: int, base_r0: float) -> float:
        """
        Compute HIT = 1 - 1/R_effective for the current variant.
        Returns as a fraction (0-1).
        """
        effective_r0 = base_r0 * self.get_r0_modifier(day)
        if effective_r0 <= 1:
            return 0.0
        return 1.0 - 1.0 / effective_r0
