#!/usr/bin/env python3
"""
Entry point for the enhanced COVID-19 Vaccine Distribution Simulation.

Usage:
    python run_simulation.py
    python run_simulation.py --config simulation_config.yaml --output-dir results
    python run_simulation.py --seed 42 --days 600
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.simulation import EnhancedSimulationConfig, EnhancedGlobalSimulation
from src.visualization.visualizer import EnhancedVisualizer
from src.analysis.equity_metrics import vaccine_gini, equity_gap


def main():
    parser = argparse.ArgumentParser(
        description='COVID-19 Vaccine Distribution Optimization Simulation (SEIR+ Model)'
    )
    parser.add_argument('--config', default='simulation_config.yaml',
                        help='Path to simulation config YAML')
    parser.add_argument('--countries', default='data/world_countries_data.csv',
                        help='Path to countries CSV')
    parser.add_argument('--vaccines', default='data/daily_vaccine_availability.csv',
                        help='Path to daily vaccine availability CSV')
    parser.add_argument('--output-dir', default='results',
                        help='Output directory for results')
    parser.add_argument('--seed', type=int, default=None,
                        help='Override random seed (default: from config)')
    parser.add_argument('--days', type=int, default=None,
                        help='Override simulation days (default: from config)')
    parser.add_argument('--no-variants', action='store_true',
                        help='Disable variant emergence')
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    print("Loading configuration...")
    config_path = Path(args.config)
    if config_path.exists():
        config = EnhancedSimulationConfig.from_yaml(str(config_path))
    else:
        print(f"  Config file {args.config} not found, using defaults")
        config = EnhancedSimulationConfig()

    # Apply CLI overrides
    if args.seed is not None:
        config.random_seed = args.seed
    if args.days is not None:
        config.simulation_days = args.days
    if args.no_variants:
        config.enable_variants = False

    # Load data
    print("Loading data files...")
    countries_data = pd.read_csv(args.countries)
    vaccines_data = pd.read_csv(args.vaccines)
    print(f"  {len(countries_data)} countries, {len(vaccines_data)} days of vaccine data")

    # Initialize and run simulation
    print("\nInitializing enhanced simulation (SEIR+ model)...")
    simulation = EnhancedGlobalSimulation(config)

    print(f"Running {len(simulation.strategies)} strategies "
          f"over {min(config.simulation_days, len(vaccines_data))} days...\n")
    results, time_series = simulation.run_all(countries_data, vaccines_data)

    # Save results
    print("\nSaving results...")
    results.to_csv(str(output_dir / 'simulation_results.csv'), index=False)
    pd.DataFrame(time_series).to_csv(str(output_dir / 'time_series_data.csv'), index=False)

    # Save analysis JSON
    analysis = _build_analysis(results)
    with open(str(output_dir / 'analysis_results.json'), 'w') as f:
        json.dump(analysis, f, indent=4, default=str)

    # Save summary text
    _write_summary(results, analysis, output_dir)

    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = EnhancedVisualizer(
        results, time_series, simulation.npi_managers, str(output_dir)
    )
    visualizer.export_all_visualizations()

    # Print summary
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {output_dir}/")
    print(f"  - simulation_results.csv")
    print(f"  - time_series_data.csv")
    print(f"  - analysis_results.json")
    print(f"  - analysis_summary.txt")
    print(f"  - Various visualization PNGs")

    print(f"\n{'Strategy':<25} {'Deaths':>12} {'Global HIT':>12} "
          f"{'Gini':>8} {'YLL':>14}")
    print("-" * 75)
    for _, row in results.iterrows():
        deaths = f"{row['total_deaths']:,.0f}" if pd.notna(row.get('total_deaths')) else 'N/A'
        hit = f"{row['days_to_70_global']}" if pd.notna(row.get('days_to_70_global')) else 'N/A'
        gini = f"{row['vaccine_gini']:.3f}" if pd.notna(row.get('vaccine_gini')) else 'N/A'
        yll = f"{row['years_of_life_lost']:,.0f}" if pd.notna(row.get('years_of_life_lost')) else 'N/A'
        print(f"  {row['strategy']:<23} {deaths:>12} {hit:>12} {gini:>8} {yll:>14}")

    print("\nDISCLAIMER: This is an educational simulation for exploring vaccine")
    print("distribution equity. Real policy requires far richer models, ethical")
    print("deliberation, and stakeholder inclusion (e.g., WHO, LMIC voices).")


def _build_analysis(results: pd.DataFrame) -> dict:
    """Build analysis dict from results."""
    metrics = ['days_to_70_global', 'days_to_70_economic', 'days_to_50_countries',
               'total_deaths', 'vaccine_gini', 'equity_gap', 'years_of_life_lost',
               'peak_hospitalized']

    baseline_name = 'population_proportional'
    baseline = results[results['strategy'] == baseline_name]
    if baseline.empty:
        baseline = results.iloc[[0]]
        baseline_name = baseline['strategy'].iloc[0]

    analysis = {
        'baseline_strategy': baseline_name,
        'metric_comparisons': {},
        'rankings': {},
        'summary_statistics': {},
    }

    for metric in metrics:
        if metric not in results.columns:
            continue

        baseline_val = baseline[metric].iloc[0]
        if pd.isna(baseline_val):
            baseline_val = 0

        comparisons = {}
        for _, row in results.iterrows():
            val = row[metric]
            if pd.isna(val):
                val = 0
            improvement = 0
            if baseline_val != 0:
                improvement = ((baseline_val - val) / abs(baseline_val)) * 100
            comparisons[row['strategy']] = {
                'value': float(val),
                'improvement': float(improvement),
            }

        analysis['metric_comparisons'][metric] = comparisons

        # Rankings (lower is better for all metrics)
        valid = results.dropna(subset=[metric])
        if not valid.empty:
            ranked = valid.sort_values(metric)
            analysis['rankings'][metric] = list(ranked['strategy'])

        # Summary statistics
        valid_vals = results[metric].dropna()
        if not valid_vals.empty:
            analysis['summary_statistics'][metric] = {
                'mean': float(valid_vals.mean()),
                'median': float(valid_vals.median()),
                'std': float(valid_vals.std()) if len(valid_vals) > 1 else 0.0,
                'min': float(valid_vals.min()),
                'max': float(valid_vals.max()),
            }

    return analysis


def _write_summary(results: pd.DataFrame, analysis: dict, output_dir: Path):
    """Write human-readable analysis summary."""
    with open(str(output_dir / 'analysis_summary.txt'), 'w') as f:
        f.write("COVID-19 Vaccine Distribution Strategy Analysis\n")
        f.write("=" * 50 + "\n")
        f.write("Model: SEIR+ with age structure, variants, per-country NPIs\n\n")

        f.write(f"Baseline Strategy: {analysis['baseline_strategy']}\n")
        f.write(f"Strategies Evaluated: {len(results)}\n\n")

        for metric, rankings in analysis.get('rankings', {}).items():
            title = metric.replace('_', ' ').title()
            f.write(f"\n{title}:\n")
            f.write("-" * len(title) + "-\n")

            comparisons = analysis['metric_comparisons'].get(metric, {})
            for i, strategy in enumerate(rankings, 1):
                info = comparisons.get(strategy, {})
                val = info.get('value', 0)
                imp = info.get('improvement', 0)
                f.write(f"  {i}. {strategy}: {val:,.1f} ({imp:+.1f}% vs baseline)\n")

            stats = analysis['summary_statistics'].get(metric, {})
            if stats:
                f.write(f"  Mean: {stats['mean']:,.1f} | "
                       f"Std: {stats['std']:,.1f} | "
                       f"Range: [{stats['min']:,.1f}, {stats['max']:,.1f}]\n")
            f.write("\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write("DISCLAIMER: This is an educational simulation. Real policy\n")
        f.write("requires far richer models and ethical deliberation.\n")


if __name__ == '__main__':
    main()
