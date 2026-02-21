"""
Per-country lockdown and NPI management with graduated response levels
and compliance decay.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Dict, List, Optional


class NPILevel(IntEnum):
    """Non-pharmaceutical intervention levels."""
    NONE = 0       # No restrictions
    MILD = 1       # Masks, distancing
    MODERATE = 2   # School closures, gathering limits
    STRICT = 3     # Full lockdown

# R0 multiplier for each NPI level
NPI_R0_MULTIPLIER = {
    NPILevel.NONE: 1.0,
    NPILevel.MILD: 0.8,
    NPILevel.MODERATE: 0.6,
    NPILevel.STRICT: 0.4,
}

# Infection rate thresholds for escalation (as fraction of population)
NPI_ESCALATION_THRESHOLDS = {
    NPILevel.MILD: 0.005,      # 0.5% infected
    NPILevel.MODERATE: 0.01,   # 1.0% infected
    NPILevel.STRICT: 0.02,     # 2.0% infected
}

# De-escalation at 80% of escalation threshold
NPI_DEESCALATION_FACTOR = 0.6


class CountryLockdownController:
    """Per-country NPI management with graduated response and compliance decay."""

    def __init__(self, country_name: str,
                 compliance_decay_rate: float = 0.005,
                 min_compliance: float = 0.4):
        self.country_name = country_name
        self.current_level = NPILevel.NONE
        self.compliance_decay_rate = compliance_decay_rate
        self.min_compliance = min_compliance

        # Track lockdown periods
        self.level_history: List[Dict] = []
        self.days_at_current_level = 0
        self.total_lockdown_days = 0  # Days at MODERATE or STRICT

    def update(self, day: int, infection_rate: float) -> float:
        """
        Update NPI level based on infection rate and return effective R0 modifier.

        Args:
            day: Current simulation day
            infection_rate: Current infection rate (infected / population)

        Returns:
            Effective R0 multiplier accounting for NPI level and compliance
        """
        previous_level = self.current_level
        new_level = self._determine_level(infection_rate)

        if new_level != self.current_level:
            self.level_history.append({
                'day': day,
                'from_level': int(self.current_level),
                'to_level': int(new_level),
            })
            self.current_level = new_level
            self.days_at_current_level = 0
        else:
            self.days_at_current_level += 1

        if self.current_level >= NPILevel.MODERATE:
            self.total_lockdown_days += 1

        # Compliance decay: people comply less over time
        compliance = self._get_compliance()
        base_modifier = NPI_R0_MULTIPLIER[self.current_level]

        # Effective modifier: blend between no-NPI (1.0) and full-NPI based on compliance
        effective_modifier = 1.0 - compliance * (1.0 - base_modifier)
        return effective_modifier

    def _determine_level(self, infection_rate: float) -> NPILevel:
        """Determine appropriate NPI level with hysteresis."""
        # Check for escalation
        if infection_rate >= NPI_ESCALATION_THRESHOLDS.get(NPILevel.STRICT, float('inf')):
            return NPILevel.STRICT
        elif infection_rate >= NPI_ESCALATION_THRESHOLDS.get(NPILevel.MODERATE, float('inf')):
            return max(self.current_level, NPILevel.MODERATE)
        elif infection_rate >= NPI_ESCALATION_THRESHOLDS.get(NPILevel.MILD, float('inf')):
            return max(self.current_level, NPILevel.MILD)

        # Check for de-escalation (hysteresis: only de-escalate below lower threshold)
        if self.current_level == NPILevel.STRICT:
            deesc = NPI_ESCALATION_THRESHOLDS[NPILevel.STRICT] * NPI_DEESCALATION_FACTOR
            if infection_rate < deesc:
                return NPILevel.MODERATE
        elif self.current_level == NPILevel.MODERATE:
            deesc = NPI_ESCALATION_THRESHOLDS[NPILevel.MODERATE] * NPI_DEESCALATION_FACTOR
            if infection_rate < deesc:
                return NPILevel.MILD
        elif self.current_level == NPILevel.MILD:
            deesc = NPI_ESCALATION_THRESHOLDS[NPILevel.MILD] * NPI_DEESCALATION_FACTOR
            if infection_rate < deesc:
                return NPILevel.NONE

        return self.current_level

    def _get_compliance(self) -> float:
        """Compliance decays over time at current NPI level."""
        if self.current_level == NPILevel.NONE:
            return 1.0
        decay = self.compliance_decay_rate * self.days_at_current_level
        return max(self.min_compliance, 1.0 - decay)

    def get_statistics(self) -> Dict:
        return {
            'country': self.country_name,
            'current_level': int(self.current_level),
            'total_lockdown_days': self.total_lockdown_days,
            'level_changes': len(self.level_history),
            'history': self.level_history,
        }


class GlobalNPIManager:
    """Manages per-country NPI controllers."""

    def __init__(self):
        self.controllers: Dict[str, CountryLockdownController] = {}

    def add_country(self, country_name: str, **kwargs) -> None:
        self.controllers[country_name] = CountryLockdownController(country_name, **kwargs)

    def update_all(self, day: int, infection_rates: Dict[str, float]) -> Dict[str, float]:
        """
        Update all countries' NPI levels and return R0 modifiers.

        Args:
            day: Current simulation day
            infection_rates: {country_name: infection_rate}

        Returns:
            {country_name: r0_modifier}
        """
        modifiers = {}
        for name, rate in infection_rates.items():
            if name in self.controllers:
                modifiers[name] = self.controllers[name].update(day, rate)
            else:
                modifiers[name] = 1.0
        return modifiers

    def get_all_statistics(self) -> Dict[str, Dict]:
        return {name: ctrl.get_statistics() for name, ctrl in self.controllers.items()}
