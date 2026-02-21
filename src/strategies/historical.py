"""
Historically-calibrated vaccine allocation strategy.

Models the actual COVID-19 vaccine distribution pattern (2021-2022), where
high-income nations pre-purchased the vast majority of early vaccine supply
through Advance Purchase Agreements (APAs), while lower-income countries
waited for COVAX — which was chronically underfunded and late.

Real-world approximate fractions of global vaccine supply received by income group
(Our World in Data / WHO data, first 12 months of rollout):
  - High-income (16% of pop)  →  ~53% of doses
  - Upper-middle              →  ~35% of doses
  - Lower-middle              →   ~9% of doses
  - Low-income (<10% of pop)  →   ~3% of doses

This strategy reproduces that skew by weighting allocation proportionally to
GNI_per_capita raised to a time-varying exponent:

  Phase 1  (days   0 – vaccine_start_day):      no vaccines available, no-op
  Phase 2  (days vaccine_start – peak_day):     exponent = rich_exponent  (strong hoarding)
  Phase 3  (days peak_day – equitable_day):     exponent linearly decays → base_exponent
  Phase 4  (days equitable_day+):               exponent = base_exponent  (near-equitable)

Phase 2 captures the first six months of rollout when wealthy nations received
the overwhelming majority of supply; Phase 3-4 capture COVAX scaling up from
mid-2021 onward.
"""

from typing import Dict
from src.strategies.base_strategy import AllocationStrategy


# Approximate simulation day when the first vaccine doses became available globally.
# Day 0 = 2019-12-31, so ~Dec 2020 = Day 366.
_DEFAULT_VACCINE_START_DAY = 366

# Day when high-income hoarding was most acute (~June 2021 = Day 548).
_DEFAULT_PEAK_HOARDING_DAY = 548

# Day from which distribution became meaningfully more equitable (~Jan 2022 = Day 732).
_DEFAULT_EQUITABLE_DAY = 732


class HistoricalWealthWeighted(AllocationStrategy):
    """
    Historically-calibrated strategy: allocates vaccines proportionally to
    GNI_per_capita^exponent, with exponent phased from high (rich-nation
    hoarding period) down to near-1 (more equitable COVAX-scale-up period).

    Parameters
    ----------
    rich_exponent : float
        GNI exponent during peak hoarding phase. A value of 2.0 means a
        country with 10× the GNI per capita gets 100× the weight per person —
        reproducing the observed 50:1 disparity in early rollout doses.
    base_exponent : float
        GNI exponent once distribution becomes more equitable (still > 1 to
        reflect residual wealth bias, but much reduced).
    vaccine_start_day : int
        Simulation day when vaccines first became globally available.
    peak_hoarding_day : int
        Simulation day when high-income hoarding peaked; exponent starts
        linearly decaying after this.
    equitable_day : int
        Simulation day when equitable exponent is fully reached.
    """

    def __init__(
        self,
        rich_exponent: float = 2.0,
        base_exponent: float = 0.6,
        vaccine_start_day: int = _DEFAULT_VACCINE_START_DAY,
        peak_hoarding_day: int = _DEFAULT_PEAK_HOARDING_DAY,
        equitable_day: int = _DEFAULT_EQUITABLE_DAY,
    ):
        self.rich_exponent = rich_exponent
        self.base_exponent = base_exponent
        self.vaccine_start_day = vaccine_start_day
        self.peak_hoarding_day = peak_hoarding_day
        self.equitable_day = equitable_day

        # Internal call counter — incremented every allocate() call so we
        # know which simulation day we are on without changing the interface.
        self._call_count = 0

    @property
    def name(self) -> str:
        return "historical_wealth_weighted"

    def _current_exponent(self) -> float:
        """Return the GNI exponent appropriate for the current simulation day."""
        day = self._call_count

        if day < self.vaccine_start_day:
            # Pre-vaccine period — strategy irrelevant (no supply).
            return self.rich_exponent

        if day <= self.peak_hoarding_day:
            # Peak hoarding: richest nations dominate.
            return self.rich_exponent

        if day >= self.equitable_day:
            # COVAX scaled up, distribution more equitable.
            return self.base_exponent

        # Linear interpolation between peak_hoarding_day and equitable_day.
        progress = (day - self.peak_hoarding_day) / (
            self.equitable_day - self.peak_hoarding_day
        )
        return self.rich_exponent + progress * (self.base_exponent - self.rich_exponent)

    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        """
        Allocate vaccines weighted by GNI_per_capita^exponent.

        Each country's weight = (GNI_per_capita + 1) ** exponent × population,
        so absolute allocation volume still scales with population, but the
        per-capita share is skewed heavily toward wealthier nations.
        """
        self._call_count += 1

        if not countries or available_vaccines <= 0:
            return {name: 0 for name in countries}

        exponent = self._current_exponent()

        # Compute wealth-skewed weights.
        weights: Dict[str, float] = {}
        for name, country in countries.items():
            gni = max(0.0, country.gni_per_capita)
            # Population × GNI_weight: captures both country size and wealth bias.
            weights[name] = country.population * ((gni + 1.0) ** exponent)

        total_weight = sum(weights.values())
        if total_weight <= 0:
            # Fallback to proportional if all weights collapse.
            total_pop = sum(c.population for c in countries.values())
            total_weight = total_pop
            weights = {n: c.population for n, c in countries.items()}

        allocations: Dict[str, int] = {}
        for name, country in countries.items():
            raw_share = int(available_vaccines * weights[name] / total_weight)
            # Respect per-country daily absorption cap and susceptible pool.
            capped = min(
                raw_share,
                country.max_daily_vaccines(),
                country.compartments.total_susceptible,
            )
            allocations[name] = max(0, capped)

        return allocations
