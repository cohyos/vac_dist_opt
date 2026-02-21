"""
SEIR+ epidemic model with age structure, hospitalization, waning immunity,
overdispersed transmission, and healthcare-capacity-dependent mortality.

Compartments per age group:
  S → E → I → R (mild recovery)
               → H → R (hospital recovery)
                    → D (death)
  R/V → W → S (waning immunity, partial re-susceptibility)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Optional


# Age group definitions: 0-17, 18-44, 45-64, 65-79, 80+
AGE_GROUPS = ['0-17', '18-44', '45-64', '65-79', '80+']
NUM_AGE_GROUPS = len(AGE_GROUPS)

# Default age distribution (global average, can be overridden per country)
DEFAULT_AGE_DISTRIBUTION = np.array([0.26, 0.33, 0.24, 0.12, 0.05])

# Default contact matrix (symmetric, relative contact rates between age groups)
# Based on Mossong et al. (2008) POLYMOD study, simplified
DEFAULT_CONTACT_MATRIX = np.array([
    [3.0, 1.5, 1.0, 0.5, 0.3],  # 0-17
    [1.5, 3.0, 2.0, 1.0, 0.5],  # 18-44
    [1.0, 2.0, 2.5, 1.5, 0.8],  # 45-64
    [0.5, 1.0, 1.5, 2.0, 1.0],  # 65-79
    [0.3, 0.5, 0.8, 1.0, 1.5],  # 80+
])

# Age-specific infection fatality rates (O'Driscoll et al. 2021)
DEFAULT_IFR_BY_AGE = np.array([0.00003, 0.0005, 0.006, 0.025, 0.09])

# Age-specific hospitalization rates
DEFAULT_HOSP_RATE_BY_AGE = np.array([0.001, 0.01, 0.04, 0.10, 0.18])


@dataclass
class EpidemicParams:
    """Parameters for the SEIR+ model."""
    # Transmission
    base_r0: float = 2.5
    overdispersion_k: float = 0.1  # Negative binomial dispersion (lower = more superspreading)

    # Timing
    incubation_period: float = 5.2      # days (E→I)
    infectious_period: float = 10.0     # days (I→R/H)
    hospital_stay: float = 10.0         # days (H→R/D)

    # Severity (age-specific arrays)
    ifr_by_age: np.ndarray = field(default_factory=lambda: DEFAULT_IFR_BY_AGE.copy())
    hosp_rate_by_age: np.ndarray = field(default_factory=lambda: DEFAULT_HOSP_RATE_BY_AGE.copy())

    # Healthcare capacity
    hospital_beds_per_capita: float = 0.003  # WHO global average
    mortality_multiplier_over_capacity: float = 2.0

    # Immunity waning
    natural_immunity_half_life: float = 180.0  # days
    vaccine_immunity_half_life: float = 150.0  # days
    waning_susceptibility: float = 0.5  # partial susceptibility after waning

    # Contact matrix
    contact_matrix: np.ndarray = field(default_factory=lambda: DEFAULT_CONTACT_MATRIX.copy())


class SEIRCompartments:
    """Manages SEIR+ compartments with age structure for a single country."""

    def __init__(self, population: int, age_distribution: np.ndarray = None,
                 initial_infected: int = 100):
        self.age_dist = age_distribution if age_distribution is not None else DEFAULT_AGE_DISTRIBUTION.copy()
        self.total_initial_pop = population

        # Initialize compartments per age group
        pop_by_age = (self.age_dist * population).astype(int)
        # Adjust rounding to match total population
        pop_by_age[-1] += population - pop_by_age.sum()

        # Distribute initial infections proportionally across age groups
        init_inf_by_age = (self.age_dist * initial_infected).astype(int)
        init_inf_by_age[-1] += initial_infected - init_inf_by_age.sum()

        self.S = pop_by_age - init_inf_by_age   # Susceptible
        self.E = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Exposed
        self.I = init_inf_by_age.copy()          # Infectious
        self.H = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Hospitalized
        self.R = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Recovered
        self.V = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Vaccinated (immune)
        self.W = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Waned immunity
        self.D = np.zeros(NUM_AGE_GROUPS, dtype=int)  # Dead

        self.N = pop_by_age.copy()  # Living population per age group

    @property
    def total_susceptible(self) -> int:
        return int(self.S.sum())

    @property
    def total_infected(self) -> int:
        return int(self.I.sum())

    @property
    def total_exposed(self) -> int:
        return int(self.E.sum())

    @property
    def total_hospitalized(self) -> int:
        return int(self.H.sum())

    @property
    def total_recovered(self) -> int:
        return int(self.R.sum())

    @property
    def total_vaccinated(self) -> int:
        return int(self.V.sum())

    @property
    def total_dead(self) -> int:
        return int(self.D.sum())

    @property
    def total_population(self) -> int:
        return int(self.N.sum())

    @property
    def total_immune(self) -> int:
        return int(self.R.sum() + self.V.sum())

    def get_immunity_percentage(self) -> float:
        if self.total_initial_pop == 0:
            return 0.0
        return (self.total_immune / self.total_initial_pop) * 100

    def verify_conservation(self) -> bool:
        """Check that S+E+I+H+R+V+W+D = initial population (per age group)."""
        total = self.S + self.E + self.I + self.H + self.R + self.V + self.W + self.D
        expected = (self.age_dist * self.total_initial_pop).astype(int)
        expected[-1] += self.total_initial_pop - expected.sum()
        return np.allclose(total, expected, atol=1)


def step_seir(compartments: SEIRCompartments, params: EpidemicParams,
              r0_modifier: float = 1.0, vaccine_efficacy: float = 0.95) -> Dict:
    """
    Advance the SEIR+ model by one day.

    Args:
        compartments: Current state of all compartments
        params: Epidemic parameters
        r0_modifier: Multiplier on R0 (e.g., from lockdown/NPI or variant)
        vaccine_efficacy: Current vaccine efficacy (may be reduced by variants)

    Returns:
        Dict with daily event counts
    """
    c = compartments
    p = params

    effective_r0 = p.base_r0 * r0_modifier
    beta = effective_r0 / p.infectious_period  # transmission rate per day

    # Transition rates
    sigma = 1.0 / p.incubation_period   # E→I rate
    gamma = 1.0 / p.infectious_period   # I→R/H rate
    delta = 1.0 / p.hospital_stay       # H→R/D rate

    # Waning rates (exponential decay from half-life)
    if p.natural_immunity_half_life > 0:
        wane_rate_natural = np.log(2) / p.natural_immunity_half_life
    else:
        wane_rate_natural = 0.0
    if p.vaccine_immunity_half_life > 0:
        wane_rate_vaccine = np.log(2) / p.vaccine_immunity_half_life
    else:
        wane_rate_vaccine = 0.0

    # Healthcare capacity check
    total_hosp = c.H.sum()
    hospital_capacity = int(c.total_initial_pop * p.hospital_beds_per_capita)
    over_capacity = total_hosp > hospital_capacity

    # === Force of infection (age-structured) ===
    # Lambda_a = beta * sum_b(C_ab * I_b / N_b) for each age group a
    infection_pressure = np.zeros(NUM_AGE_GROUPS)
    for a in range(NUM_AGE_GROUPS):
        for b in range(NUM_AGE_GROUPS):
            if c.N[b] > 0:
                infection_pressure[a] += p.contact_matrix[a, b] * c.I[b] / c.N[b]
        infection_pressure[a] *= beta

    # === New exposures (S→E) using negative binomial for overdispersion ===
    new_exposed = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.S[a] > 0 and infection_pressure[a] > 0:
            mean_new = infection_pressure[a] * c.S[a]
            if mean_new > 0 and p.overdispersion_k > 0:
                # Negative binomial: mean=mean_new, var=mean_new + mean_new^2/k
                p_nb = p.overdispersion_k / (p.overdispersion_k + mean_new)
                try:
                    new_exp = np.random.negative_binomial(p.overdispersion_k, p_nb)
                except ValueError:
                    new_exp = np.random.poisson(mean_new)
            else:
                new_exp = np.random.poisson(max(0, mean_new))
            new_exposed[a] = min(new_exp, c.S[a])

    # Also expose waned individuals (partial susceptibility)
    new_exposed_waned = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.W[a] > 0 and infection_pressure[a] > 0:
            mean_w = infection_pressure[a] * c.W[a] * p.waning_susceptibility
            new_exposed_waned[a] = min(np.random.poisson(max(0, mean_w)), c.W[a])

    # === E→I (incubation complete) ===
    new_infectious = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.E[a] > 0:
            new_infectious[a] = np.random.binomial(c.E[a], min(1.0, sigma))

    # === I→H (hospitalization) and I→R (mild recovery) ===
    new_hospitalized = np.zeros(NUM_AGE_GROUPS, dtype=int)
    new_recovered_mild = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.I[a] > 0:
            # Probability of leaving I compartment this day
            leaving_I = np.random.binomial(c.I[a], min(1.0, gamma))
            # Of those leaving, fraction goes to hospital
            new_hospitalized[a] = np.random.binomial(leaving_I, p.hosp_rate_by_age[a])
            new_recovered_mild[a] = leaving_I - new_hospitalized[a]

    # === H→D (death) and H→R (hospital recovery) ===
    new_deaths = np.zeros(NUM_AGE_GROUPS, dtype=int)
    new_recovered_hosp = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.H[a] > 0:
            leaving_H = np.random.binomial(c.H[a], min(1.0, delta))
            # Case fatality among hospitalized, adjusted for capacity
            base_cfr = p.ifr_by_age[a] / max(0.001, p.hosp_rate_by_age[a])
            if over_capacity:
                cfr = min(1.0, base_cfr * p.mortality_multiplier_over_capacity)
            else:
                cfr = min(1.0, base_cfr)
            new_deaths[a] = np.random.binomial(leaving_H, cfr)
            new_recovered_hosp[a] = leaving_H - new_deaths[a]

    # === Immunity waning: R→W and V→W ===
    new_waned_natural = np.zeros(NUM_AGE_GROUPS, dtype=int)
    new_waned_vaccine = np.zeros(NUM_AGE_GROUPS, dtype=int)
    for a in range(NUM_AGE_GROUPS):
        if c.R[a] > 0 and wane_rate_natural > 0:
            new_waned_natural[a] = np.random.binomial(c.R[a], min(1.0, wane_rate_natural))
        if c.V[a] > 0 and wane_rate_vaccine > 0:
            new_waned_vaccine[a] = np.random.binomial(c.V[a], min(1.0, wane_rate_vaccine))

    # === Update compartments ===
    c.S = np.maximum(0, c.S - new_exposed)
    c.E = np.maximum(0, c.E + new_exposed + new_exposed_waned - new_infectious)
    c.I = np.maximum(0, c.I + new_infectious - new_hospitalized - new_recovered_mild)
    c.H = np.maximum(0, c.H + new_hospitalized - new_deaths - new_recovered_hosp)
    c.R = np.maximum(0, c.R + new_recovered_mild + new_recovered_hosp - new_waned_natural)
    c.V = np.maximum(0, c.V - new_waned_vaccine)
    c.W = np.maximum(0, c.W - new_exposed_waned + new_waned_natural + new_waned_vaccine)
    c.D = c.D + new_deaths
    c.N = np.maximum(0, c.N - new_deaths)

    return {
        'new_exposed': int(new_exposed.sum()),
        'new_infectious': int(new_infectious.sum()),
        'new_hospitalized': int(new_hospitalized.sum()),
        'new_recovered': int(new_recovered_mild.sum() + new_recovered_hosp.sum()),
        'new_deaths': int(new_deaths.sum()),
        'new_waned': int(new_waned_natural.sum() + new_waned_vaccine.sum()),
        'total_hospitalized': int(c.H.sum()),
        'over_capacity': over_capacity,
    }
