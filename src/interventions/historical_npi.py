"""
Historical NPI (Non-Pharmaceutical Intervention) Manager.

Loads real-world per-country lockdown schedules from a CSV data file and
overrides the infection-rate-triggered NPI model with historically-accurate
NPI levels for each country and simulation day.

For countries/days not covered by historical data, the manager falls back to
the standard infection-rate-triggered CountryLockdownController.

Data file format (data/country_lockdown_data.csv)
--------------------------------------------------
Country,start_day,end_day,npi_level,wave,notes

  Country   : must match world_countries_data.csv Country column
  start_day : inclusive start (Day 0 = 2019-12-31)
  end_day   : inclusive end
  npi_level : 0=NONE, 1=MILD, 2=MODERATE, 3=STRICT
  wave      : informational label (ignored by loader)
  notes     : informational (ignored by loader)

Lines beginning with '#' are treated as comments.

NPI → R0 multiplier mapping
----------------------------
  NONE     (0) → 1.00  (no change)
  MILD     (1) → 0.80  (masks, distancing: ~20% reduction)
  MODERATE (2) → 0.60  (school+gathering closures: ~40% reduction)
  STRICT   (3) → 0.40  (stay-at-home / full lockdown: ~60% reduction)

Compliance decay is applied on top of the base multiplier: people comply less
over time at the same NPI level, so a 30-day STRICT lockdown gradually drifts
from R0×0.40 → R0×0.56 (min compliance = 0.40).
"""

import csv
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from src.interventions.lockdown_controller import (
    CountryLockdownController,
    GlobalNPIManager,
    NPILevel,
    NPI_R0_MULTIPLIER,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class NPIPeriod:
    """A single NPI period for a country."""

    __slots__ = ("start_day", "end_day", "level")

    def __init__(self, start_day: int, end_day: int, level: NPILevel):
        self.start_day = start_day
        self.end_day = end_day
        self.level = level

    def contains(self, day: int) -> bool:
        return self.start_day <= day <= self.end_day


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_lockdown_data(csv_path: str) -> Dict[str, List[NPIPeriod]]:
    """
    Parse the historical lockdown CSV and return a dict mapping
    {country_name: [NPIPeriod, ...]} sorted by start_day.

    Comment lines (starting with '#') are skipped.
    Header row is skipped automatically.
    Rows with invalid values are skipped with a warning.
    """
    data: Dict[str, List[NPIPeriod]] = defaultdict(list)

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for lineno, row in enumerate(reader, start=1):
                # Skip blank lines and comment lines
                if not row or row[0].strip().startswith("#"):
                    continue
                # Skip header
                if lineno == 1 and row[0].strip().lower() == "country":
                    continue

                try:
                    country = row[0].strip()
                    start_day = int(row[1].strip())
                    end_day = int(row[2].strip())
                    npi_level_int = int(row[3].strip())
                except (IndexError, ValueError) as exc:
                    print(
                        f"  [HistoricalNPI] Skipping malformed row {lineno}: {exc}"
                    )
                    continue

                if npi_level_int not in (0, 1, 2, 3):
                    print(
                        f"  [HistoricalNPI] Invalid NPI level {npi_level_int} "
                        f"on row {lineno} — skipping."
                    )
                    continue

                level = NPILevel(npi_level_int)
                data[country].append(NPIPeriod(start_day, end_day, level))

    except FileNotFoundError:
        print(
            f"  [HistoricalNPI] WARNING: Lockdown data file not found: {csv_path}\n"
            f"  Falling back entirely to infection-rate NPI model."
        )
        return {}

    # Sort periods by start_day for efficient lookup
    for country in data:
        data[country].sort(key=lambda p: p.start_day)

    n_countries = len(data)
    n_periods = sum(len(v) for v in data.values())
    print(
        f"  [HistoricalNPI] Loaded {n_periods} NPI periods "
        f"for {n_countries} countries from: {csv_path}"
    )
    return dict(data)


# ---------------------------------------------------------------------------
# Per-country historical controller
# ---------------------------------------------------------------------------

class HistoricalCountryNPIController:
    """
    Applies historically-observed NPI schedules for a single country.

    On each day:
      1. Looks up the historical NPI period that covers this day.
      2. If found, uses that NPI level (with compliance decay for long periods).
      3. If not found, falls back to infection-rate-triggered logic.
    """

    def __init__(
        self,
        country_name: str,
        historical_periods: List[NPIPeriod],
        compliance_decay_rate: float = 0.004,
        min_compliance: float = 0.40,
    ):
        self.country_name = country_name
        self._periods = historical_periods  # sorted by start_day

        # Fallback controller for days without historical data
        self._fallback = CountryLockdownController(
            country_name,
            compliance_decay_rate=compliance_decay_rate,
            min_compliance=min_compliance,
        )

        # Compliance tracking for current historical period
        self._current_period: Optional[NPIPeriod] = None
        self._days_in_period: int = 0
        self._compliance_decay_rate = compliance_decay_rate
        self._min_compliance = min_compliance

    def _lookup(self, day: int) -> Optional[NPIPeriod]:
        """Return the first historical period that covers `day`, or None."""
        for period in self._periods:
            if period.start_day > day:
                break
            if period.contains(day):
                return period
        return None

    def update(self, day: int, infection_rate: float) -> float:
        """
        Return the effective R0 modifier for this country on this day.

        Uses historical data when available; falls back to infection-rate model.
        """
        period = self._lookup(day)

        if period is None:
            # No historical data — use the infection-rate controller
            self._current_period = None
            self._days_in_period = 0
            return self._fallback.update(day, infection_rate)

        # Track how long we've been in this period (for compliance decay)
        if period is not self._current_period:
            self._current_period = period
            self._days_in_period = 0
        else:
            self._days_in_period += 1

        level = period.level

        if level == NPILevel.NONE:
            return NPI_R0_MULTIPLIER[NPILevel.NONE]

        # Compliance decay: restrictions become less effective over time
        decay = self._compliance_decay_rate * self._days_in_period
        compliance = max(self._min_compliance, 1.0 - decay)

        base_modifier = NPI_R0_MULTIPLIER[level]
        # Effective modifier: linearly blend between NPI-off (1.0) and NPI-on
        # weighted by compliance
        effective_modifier = 1.0 - compliance * (1.0 - base_modifier)
        return effective_modifier

    def get_current_level(self, day: int) -> NPILevel:
        period = self._lookup(day)
        if period is not None:
            return period.level
        return self._fallback.current_level


# ---------------------------------------------------------------------------
# Global historical NPI manager
# ---------------------------------------------------------------------------

class HistoricalNPIManager:
    """
    Drop-in replacement for GlobalNPIManager that uses historically-observed
    per-country NPI schedules from a lockdown data CSV.

    For any country or day not covered by the historical data, falls back to
    the standard infection-rate-triggered NPI model.

    Usage
    -----
        mgr = HistoricalNPIManager("data/country_lockdown_data.csv")
        for name in countries:
            mgr.add_country(name)
        r0_mods = mgr.update_all(day, infection_rates)
    """

    def __init__(self, lockdown_csv_path: str):
        self._lockdown_data = load_lockdown_data(lockdown_csv_path)
        self._controllers: Dict[str, HistoricalCountryNPIController] = {}

    def add_country(self, country_name: str, **kwargs) -> None:
        periods = self._lockdown_data.get(country_name, [])
        self._controllers[country_name] = HistoricalCountryNPIController(
            country_name, periods, **kwargs
        )

    def update_all(
        self, day: int, infection_rates: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Update all country NPI levels and return {country: r0_modifier}.

        Args:
            day             : Current simulation day
            infection_rates : {country_name: infection_rate (fraction)}

        Returns:
            {country_name: r0_modifier}
        """
        modifiers: Dict[str, float] = {}
        for name, rate in infection_rates.items():
            if name in self._controllers:
                modifiers[name] = self._controllers[name].update(day, rate)
            else:
                # Country not registered — no NPI
                modifiers[name] = 1.0
        return modifiers

    def get_all_statistics(self) -> Dict:
        """Return per-country NPI statistics (for visualisation)."""
        return {
            name: {
                "country": name,
                "historical_periods": len(
                    self._lockdown_data.get(name, [])
                ),
                "fallback_total_lockdown_days": ctrl._fallback.total_lockdown_days,
            }
            for name, ctrl in self._controllers.items()
        }

    # Make it quack like GlobalNPIManager for visualiser compatibility
    @property
    def controllers(self) -> Dict:
        """Expose underlying controllers dict (for visualiser compatibility)."""
        return self._controllers
