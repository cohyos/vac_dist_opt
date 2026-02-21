#!/usr/bin/env python3
"""
Real-World Calibrated COVID-19 Vaccine Distribution Simulation
==============================================================

This script runs the SEIR+ simulation calibrated to match the actual
COVID-19 pandemic trajectory (Jan 2020 – Dec 2021) and compares the
historically-observed vaccine distribution pattern against alternative
strategies.

Real-world context
------------------
  * Original strain emerged China, December 2019.
  * WHO declared global pandemic March 11, 2020 (Day 71).
  * First vaccines authorised December 2020 (Day 366).
  * COVAX intended to supply 20% coverage to LMICs but was chronically
    underfunded; high-income nations secured bilateral APAs covering
    3-5x their population need.
  * Variants:  Alpha ~Day 120 | Delta ~Day 450 | Omicron ~Day 700.
  * NPIs: Per-country real-world lockdown schedules loaded from
    data/country_lockdown_data.csv (Oxford OxCGRT-calibrated).

Strategies compared
-------------------
  historical_wealth_weighted  - mirrors the ACTUAL 2020-2021 rollout;
                                GNI^2-weighted allocation (rich nations first)
                                phasing toward equitable from 2022.

  population_proportional     - every country receives doses proportional
                                to population (idealized baseline).

  covax_like                  - COVAX-as-intended: ensure 20% floor
                                coverage everywhere first, then proportional.

  infection_rate_based        - direct vaccines toward countries with the
                                highest active infection rates.

  mortality_risk_based        - prioritise countries with overloaded
                                hospitals (highest excess death risk).

Historical NPI integration
--------------------------
  For the historical strategy run, per-country NPIs are driven by the
  real-world lockdown schedule (data/country_lockdown_data.csv) rather
  than the model's infection-rate triggers.  Countries not present in the
  data file fall back to the infection-rate NPI model automatically.

Usage
-----
    python run_realworld_simulation.py
    python run_realworld_simulation.py --output-dir results/realworld --seed 2020
    python run_realworld_simulation.py --no-variants  # Original strain only
    python run_realworld_simulation.py --days 365     # First year only
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

# project imports
from src.simulation import EnhancedSimulationConfig, EnhancedGlobalSimulation
from src.visualization.visualizer import EnhancedVisualizer
from src.models.variant_model import VariantManager, DEFAULT_VARIANTS
from src.interventions.lockdown_controller import GlobalNPIManager
from src.interventions.historical_npi import HistoricalNPIManager
from src.strategies.base_strategy import AllocationStrategy
from src.strategies.historical import HistoricalWealthWeighted
from src.strategies.proportional import PopulationProportional
from src.strategies.needs_based import InfectionRateBased, COVAXLike, MortalityRiskBased
from src.analysis.equity_metrics import vaccine_gini, equity_gap, years_of_life_lost


# ---------------------------------------------------------------------------
# Real-World Simulation Class
# ---------------------------------------------------------------------------

class RealWorldSimulation(EnhancedGlobalSimulation):
    """
    Extends EnhancedGlobalSimulation to support historically-calibrated NPIs.

    When a strategy is designated as "historical", it uses the
    HistoricalNPIManager (real-world lockdown schedule from CSV) instead
    of the default infection-rate-triggered GlobalNPIManager.

    All other strategies still use the default model-driven NPIs, representing
    a counterfactual (same or adaptive NPI policy under a different vax strategy).
    """

    def __init__(
        self,
        config: EnhancedSimulationConfig,
        lockdown_csv: str,
        historical_strategy_names: Optional[List[str]] = None,
    ):
        super().__init__(config)
        self._lockdown_csv = lockdown_csv
        self._historical_strategy_names = set(historical_strategy_names or [])

    def _run_single_strategy(
        self,
        countries_data: pd.DataFrame,
        vaccines_data: pd.DataFrame,
        strategy: AllocationStrategy,
    ) -> Tuple[Dict, List[Dict]]:
        """
        Override: wire in historical NPI manager for designated strategies,
        infection-rate model for all others.
        """
        countries = self._init_countries(countries_data)
        num_countries = len(countries)

        # Choose NPI manager based on strategy
        if strategy.name in self._historical_strategy_names:
            npi_manager = HistoricalNPIManager(self._lockdown_csv)
            for name in countries:
                npi_manager.add_country(name)
            print("    [NPI] Using HISTORICAL lockdown schedules from CSV")
        else:
            npi_manager = GlobalNPIManager()
            for name in countries:
                npi_manager.add_country(name)

        # Fresh variant manager for this strategy run
        variant_mgr = VariantManager(
            DEFAULT_VARIANTS.copy() if self.config.enable_variants else None
        )

        time_series = []
        simulation_days = min(self.config.simulation_days, len(vaccines_data))

        for day in tqdm(range(simulation_days), desc=strategy.name, leave=False):
            available_vaccines = max(
                0, int(vaccines_data.iloc[day]["available_vaccines"])
            )

            # Allocate and administer vaccines
            allocations = strategy.allocate(countries, available_vaccines)
            for name, num_vax in allocations.items():
                if num_vax > 0:
                    countries[name].vaccinate(day, num_vax)

            # Per-country infection rates for NPI decisions
            infection_rates = {
                name: (
                    country.compartments.total_infected
                    / max(1, country.compartments.total_population)
                )
                for name, country in countries.items()
            }

            # Update NPIs and step epidemic
            r0_modifiers = npi_manager.update_all(day, infection_rates)
            for name, country in countries.items():
                npi_mod = r0_modifiers.get(name, 1.0)
                country.update(day, npi_mod, variant_mgr)

            stats = self._collect_stats(countries, day, strategy.name, variant_mgr)
            time_series.append(stats)

        # Store NPI manager reference for visualiser
        self.npi_managers[strategy.name] = npi_manager

        # Analyse results
        final_stats = self._analyze_results(time_series, strategy.name, num_countries)
        final_stats["vaccine_gini"] = vaccine_gini(countries)
        final_stats["equity_gap"] = equity_gap(countries)
        final_stats["years_of_life_lost"] = years_of_life_lost(countries)

        return final_stats, time_series


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _build_analysis(results: pd.DataFrame) -> dict:
    """Build structured analysis dict from strategy results."""
    metrics = [
        "days_to_70_global",
        "days_to_70_economic",
        "days_to_50_countries",
        "total_deaths",
        "vaccine_gini",
        "equity_gap",
        "years_of_life_lost",
        "peak_hospitalized",
    ]

    baseline_name = "population_proportional"
    baseline = results[results["strategy"] == baseline_name]
    if baseline.empty:
        baseline = results.iloc[[0]]
        baseline_name = baseline["strategy"].iloc[0]

    analysis: dict = {
        "baseline_strategy": baseline_name,
        "metric_comparisons": {},
        "rankings": {},
        "summary_statistics": {},
        "realworld_note": (
            "historical_wealth_weighted uses real per-country lockdown schedules "
            "(Oxford OxCGRT-calibrated). Other strategies use infection-rate "
            "NPI model as a counterfactual."
        ),
    }

    for metric in metrics:
        if metric not in results.columns:
            continue

        baseline_val = baseline[metric].iloc[0]
        if pd.isna(baseline_val):
            baseline_val = 0.0

        comparisons: dict = {}
        for _, row in results.iterrows():
            val = row[metric]
            if pd.isna(val):
                val = 0.0
            improvement = 0.0
            if baseline_val != 0:
                improvement = ((baseline_val - val) / abs(baseline_val)) * 100.0
            comparisons[row["strategy"]] = {
                "value": float(val),
                "improvement_vs_baseline_pct": float(improvement),
            }
        analysis["metric_comparisons"][metric] = comparisons

        valid = results.dropna(subset=[metric])
        if not valid.empty:
            analysis["rankings"][metric] = list(valid.sort_values(metric)["strategy"])

        valid_vals = results[metric].dropna()
        if not valid_vals.empty:
            analysis["summary_statistics"][metric] = {
                "mean": float(valid_vals.mean()),
                "median": float(valid_vals.median()),
                "std": float(valid_vals.std()) if len(valid_vals) > 1 else 0.0,
                "min": float(valid_vals.min()),
                "max": float(valid_vals.max()),
            }

    return analysis


def _write_summary(results: pd.DataFrame, analysis: dict, output_dir: Path) -> None:
    """Write a human-readable plain-text summary."""
    with open(str(output_dir / "realworld_summary.txt"), "w") as f:
        f.write("COVID-19 Real-World Calibrated Simulation -- Strategy Comparison\n")
        f.write("=" * 65 + "\n")
        f.write(
            "Model: SEIR+ | Age structure | "
            "Variants (Original->Alpha->Delta->Omicron)\n"
        )
        f.write("Period: Jan 2020 - Dec 2021 (730 days)\n")
        f.write(
            "NPIs:   historical_wealth_weighted -> real lockdown schedules\n"
            "        all other strategies       -> infection-rate model (counterfactual)\n\n"
        )

        f.write("Strategies\n")
        f.write("----------\n")
        lines = [
            ("historical_wealth_weighted",
             "ACTUAL 2020-2021 rollout (GNI^2-weighted; real NPI schedules)"),
            ("population_proportional", "Idealized equitable baseline"),
            ("covax_like",              "COVAX-as-intended (20% floor first)"),
            ("infection_rate_based",    "Direct doses to hotspots"),
            ("mortality_risk_based",    "Prioritise overloaded health systems"),
        ]
        for name, desc in lines:
            f.write(f"  {name:<32}  {desc}\n")
        f.write(f"\nComparison baseline: {analysis['baseline_strategy']}\n\n")

        for metric, rankings in analysis.get("rankings", {}).items():
            title = metric.replace("_", " ").title()
            f.write(f"{title}\n")
            f.write("-" * len(title) + "\n")
            comparisons = analysis["metric_comparisons"].get(metric, {})
            for i, strategy in enumerate(rankings, 1):
                info = comparisons.get(strategy, {})
                val = info.get("value", 0.0)
                imp = info.get("improvement_vs_baseline_pct", 0.0)
                tag = (
                    "  <- HISTORICAL (actual rollout)"
                    if strategy == "historical_wealth_weighted"
                    else ""
                )
                f.write(
                    f"  {i}. {strategy}: {val:,.1f}  "
                    f"({imp:+.1f}% vs baseline){tag}\n"
                )
            stats = analysis["summary_statistics"].get(metric, {})
            if stats:
                f.write(
                    f"  Mean: {stats['mean']:,.1f} | "
                    f"Std: {stats['std']:,.1f} | "
                    f"Range: [{stats['min']:,.1f}, {stats['max']:,.1f}]\n"
                )
            f.write("\n")

        f.write("=" * 65 + "\n")
        f.write(
            "DISCLAIMER: Educational simulation. Real policy requires far\n"
            "richer models, ethical deliberation, and stakeholder inclusion.\n"
        )

    print(f"  Wrote: {output_dir / 'realworld_summary.txt'}")


def _print_final_table(results: pd.DataFrame) -> None:
    """Print a compact comparison table to stdout."""
    print()
    print("=" * 95)
    print("REAL-WORLD SIMULATION RESULTS")
    print("=" * 95)
    print(
        f"  {'Strategy':<32} {'Deaths':>12} {'Days->HIT':>10} "
        f"{'Gini':>8} {'YLL (M)':>10}  Notes"
    )
    print("  " + "-" * 85)

    for _, row in results.iterrows():
        strategy = row["strategy"]
        deaths = (
            f"{row['total_deaths']:,.0f}"
            if pd.notna(row.get("total_deaths"))
            else "N/A"
        )
        hit = (
            f"{row['days_to_70_global']}"
            if pd.notna(row.get("days_to_70_global"))
            else ">730"
        )
        gini = (
            f"{row['vaccine_gini']:.3f}"
            if pd.notna(row.get("vaccine_gini"))
            else "N/A"
        )
        yll_m = (
            f"{row['years_of_life_lost'] / 1e6:.2f}M"
            if pd.notna(row.get("years_of_life_lost"))
            else "N/A"
        )
        marker = "<- ACTUAL HISTORY" if strategy == "historical_wealth_weighted" else ""
        print(
            f"  {strategy:<32} {deaths:>12} {hit:>10} "
            f"{gini:>8} {yll_m:>10}  {marker}"
        )

    print()
    print("  Gini = 0.0  -> perfectly equal per-capita vaccine distribution.")
    print("  YLL         -> Years of Life Lost (millions); lower is better.")
    print(
        "  Days->HIT   -> days until global population-weighted immunity "
        "reached the variant-adjusted herd immunity threshold."
    )
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a real-world calibrated COVID-19 vaccine distribution simulation.\n"
            "Compares the historical wealth-weighted rollout (with real lockdown\n"
            "schedules) against equitable counterfactual strategies."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", default="realworld_config.yaml",
        help="Config YAML (default: realworld_config.yaml)",
    )
    parser.add_argument(
        "--countries", default="data/world_countries_data.csv",
        help="Countries CSV",
    )
    parser.add_argument(
        "--vaccines", default="data/daily_vaccine_availability.csv",
        help="Daily vaccine availability CSV",
    )
    parser.add_argument(
        "--lockdowns", default="data/country_lockdown_data.csv",
        help="Per-country historical lockdown schedule CSV",
    )
    parser.add_argument(
        "--output-dir", default="results/realworld",
        help="Output directory (default: results/realworld)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Override random seed (default: 2020 from config)",
    )
    parser.add_argument(
        "--days", type=int, default=None,
        help="Override simulation days (default: 730 from config)",
    )
    parser.add_argument(
        "--no-variants", action="store_true",
        help="Disable variant emergence (Original strain only)",
    )
    args = parser.parse_args()

    # output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # load config
    print("Loading real-world calibrated configuration...")
    config_path = Path(args.config)
    if config_path.exists():
        config = EnhancedSimulationConfig.from_yaml(str(config_path))
        print(f"  Config     : {config_path}")
    else:
        print(
            f"  WARNING: {args.config} not found -- using defaults.\n"
            "  Run from project root: /home/user/vac_dist_opt/"
        )
        config = EnhancedSimulationConfig(
            simulation_days=730,
            random_seed=2020,
            initial_infected_per_country=500,
            enable_variants=True,
        )

    if args.seed is not None:
        config.random_seed = args.seed
    if args.days is not None:
        config.simulation_days = args.days
    if args.no_variants:
        config.enable_variants = False
        print("  Variants DISABLED -- running with Original strain only.")

    # load data
    print("Loading data files...")
    try:
        countries_data = pd.read_csv(args.countries)
        vaccines_data = pd.read_csv(args.vaccines)
    except FileNotFoundError as exc:
        print(f"  ERROR: {exc}")
        print("  Ensure you run from the project root: /home/user/vac_dist_opt/")
        sys.exit(1)

    effective_days = min(config.simulation_days, len(vaccines_data))
    print(f"  Countries  : {len(countries_data)}")
    print(f"  Sim days   : {effective_days}  (Day 0 = 2019-12-31)")
    print(f"  Seed       : {config.random_seed}")
    print(f"  Lockdowns  : {args.lockdowns}")

    # build simulation
    print("\nInitialising real-world simulation (SEIR+ model)...")
    simulation = RealWorldSimulation(
        config=config,
        lockdown_csv=args.lockdowns,
        historical_strategy_names=["historical_wealth_weighted"],
    )

    # Define the focused real-world strategy set
    simulation.strategies = [
        # Historically-calibrated "actual rollout"
        HistoricalWealthWeighted(
            rich_exponent=2.0,       # GNI^2 weighting: captures 50:1 per-capita disparity
            base_exponent=0.6,       # Late-phase near-equitable (COVAX scaled up)
            vaccine_start_day=366,   # Vaccines first available globally (Dec 2020)
            peak_hoarding_day=548,   # Peak hoarding by rich nations (~Jun 2021)
            equitable_day=732,       # Distribution more equitable from ~Jan 2022
        ),
        # Counterfactual alternatives
        PopulationProportional(),
        COVAXLike(floor_coverage=0.20),
        InfectionRateBased(),
        MortalityRiskBased(),
    ]

    print(f"\nRunning {len(simulation.strategies)} strategies over {effective_days} days:\n")
    for s in simulation.strategies:
        npi_tag = (
            "  [historical NPI: real lockdown schedules]"
            if s.name == "historical_wealth_weighted"
            else "  [model NPI: infection-rate triggered]"
        )
        print(f"  * {s.name}{npi_tag}")
    print()

    # run simulation
    results, time_series = simulation.run_all(countries_data, vaccines_data)

    # save outputs
    print("\nSaving results...")
    results.to_csv(str(output_dir / "simulation_results.csv"), index=False)
    pd.DataFrame(time_series).to_csv(str(output_dir / "time_series_data.csv"), index=False)
    print(f"  Wrote: {output_dir / 'simulation_results.csv'}")
    print(f"  Wrote: {output_dir / 'time_series_data.csv'}")

    analysis = _build_analysis(results)
    with open(str(output_dir / "analysis_results.json"), "w") as f:
        json.dump(analysis, f, indent=4, default=str)
    print(f"  Wrote: {output_dir / 'analysis_results.json'}")

    _write_summary(results, analysis, output_dir)

    # visualisations
    print("\nGenerating visualisations...")
    try:
        visualizer = EnhancedVisualizer(
            results, time_series, simulation.npi_managers, str(output_dir)
        )
        visualizer.export_all_visualizations()
        print("  Visualisations saved.")
    except Exception as exc:
        print(f"  WARNING: Visualisation failed: {exc}")
        print("  Results CSV and JSON were saved successfully.")

    # final table
    _print_final_table(results)

    print(f"All outputs written to: {output_dir}/\n")
    print(
        "KEY INSIGHT\n"
        "  Compare 'historical_wealth_weighted' (actual rollout, real lockdowns)\n"
        "  against 'covax_like' and 'population_proportional' to quantify the\n"
        "  human cost of the observed inequitable vaccine distribution.\n"
    )
    print(
        "DISCLAIMER: Educational simulation for exploring vaccine equity.\n"
        "Real policy requires far richer models, ethical deliberation, and\n"
        "stakeholder inclusion (WHO, LMIC governments, civil society)."
    )


if __name__ == "__main__":
    main()
