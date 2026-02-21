"""
Enhanced visualization suite for the SEIR+ vaccine distribution simulation.

Generates plots for strategy comparison, immunity progression, lockdown periods,
equity metrics, and variant timeline.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict, List, Optional


class EnhancedVisualizer:
    """Generates all visualizations for the enhanced simulation."""

    def __init__(self, results_df: pd.DataFrame, time_series_data: List[Dict],
                 npi_managers: Dict = None, output_dir: str = 'results'):
        self.results = results_df
        self.time_series = pd.DataFrame(time_series_data)
        self.npi_managers = npi_managers or {}
        self.output_dir = output_dir

        plt.rcParams.update({
            'figure.figsize': [12, 8],
            'axes.grid': True,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'font.size': 10,
            'lines.linewidth': 2,
        })

    def _save_fig(self, filename: str) -> None:
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()

    def create_metric_comparison_plot(self) -> None:
        """Bar charts comparing strategies across key metrics."""
        metrics = [
            ('days_to_70_global', 'Days to Global Herd Immunity'),
            ('days_to_70_economic', 'Days to Economic Herd Immunity'),
            ('days_to_50_countries', 'Days to 50% Countries Immune'),
            ('total_deaths', 'Total Deaths'),
        ]

        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        axes = axes.ravel()

        for idx, (metric, title) in enumerate(metrics):
            if metric not in self.results.columns:
                continue

            data = self.results.dropna(subset=[metric]).sort_values(metric)
            if data.empty:
                axes[idx].text(0.5, 0.5, f'No data for {title}',
                              ha='center', va='center', transform=axes[idx].transAxes)
                continue

            values = data[metric].astype(float)
            bars = axes[idx].bar(range(len(data)), values, color='steelblue', alpha=0.8)
            axes[idx].set_xticks(range(len(data)))
            axes[idx].set_xticklabels(data['strategy'], rotation=45, ha='right', fontsize=8)
            axes[idx].set_title(title, fontsize=12)

            for i, v in enumerate(values):
                if pd.notna(v):
                    label = f'{v:,.0f}' if v > 1000 else f'{v:.1f}'
                    axes[idx].text(i, v, label, ha='center', va='bottom', fontsize=7)

        plt.suptitle('Strategy Comparison Across Key Metrics', fontsize=14, y=1.01)
        plt.tight_layout()
        self._save_fig('strategy_metrics_comparison.png')

    def create_timeline_plot(self) -> None:
        """Line chart of immunity progression over time by strategy."""
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))

        colors = plt.cm.tab10.colors
        strategies = self.results['strategy'].unique()

        # Global immunity
        for idx, strategy in enumerate(strategies):
            sdata = self.time_series[self.time_series['strategy'] == strategy]
            if 'global_immunity_percentage' in sdata.columns and not sdata.empty:
                axes[0].plot(sdata['day'],
                           sdata['global_immunity_percentage'].astype(float),
                           label=strategy, color=colors[idx % len(colors)], alpha=0.8)

        if 'herd_immunity_threshold' in self.time_series.columns:
            # Plot dynamic HIT from first strategy
            first_strategy = strategies[0]
            sdata = self.time_series[self.time_series['strategy'] == first_strategy]
            if not sdata.empty:
                axes[0].plot(sdata['day'],
                           sdata['herd_immunity_threshold'].astype(float),
                           color='red', linestyle='--', linewidth=1.5,
                           label='Dynamic HIT')

        axes[0].set_title('Global Immunity Progression by Strategy')
        axes[0].set_xlabel('Days')
        axes[0].set_ylabel('Global Immunity (%)')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

        # Infection rate
        for idx, strategy in enumerate(strategies):
            sdata = self.time_series[self.time_series['strategy'] == strategy]
            if 'infection_rate' in sdata.columns and not sdata.empty:
                axes[1].plot(sdata['day'],
                           sdata['infection_rate'].astype(float),
                           label=strategy, color=colors[idx % len(colors)], alpha=0.8)

        axes[1].set_title('Global Infection Rate by Strategy')
        axes[1].set_xlabel('Days')
        axes[1].set_ylabel('Infection Rate (%)')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

        plt.tight_layout()
        self._save_fig('immunity_progression.png')

    def create_deaths_plot(self) -> None:
        """Cumulative deaths over time by strategy."""
        fig, ax = plt.subplots(figsize=(15, 8))
        colors = plt.cm.tab10.colors
        strategies = self.results['strategy'].unique()

        for idx, strategy in enumerate(strategies):
            sdata = self.time_series[self.time_series['strategy'] == strategy]
            if 'total_deaths' in sdata.columns and not sdata.empty:
                ax.plot(sdata['day'],
                       sdata['total_deaths'].astype(float),
                       label=strategy, color=colors[idx % len(colors)], alpha=0.8)

        ax.set_title('Cumulative Deaths by Strategy')
        ax.set_xlabel('Days')
        ax.set_ylabel('Total Deaths')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        plt.tight_layout()
        self._save_fig('cumulative_deaths.png')

    def create_equity_comparison_plot(self) -> None:
        """Bar chart of equity metrics across strategies."""
        equity_metrics = [
            ('vaccine_gini', 'Vaccine Gini Coefficient\n(lower = more equitable)'),
            ('equity_gap', 'Equity Gap (Top/Bottom 10 GNI)\n(closer to 1 = more equitable)'),
            ('years_of_life_lost', 'Years of Life Lost'),
        ]

        available = [(m, t) for m, t in equity_metrics if m in self.results.columns]
        if not available:
            return

        n = len(available)
        fig, axes = plt.subplots(1, n, figsize=(7 * n, 6))
        if n == 1:
            axes = [axes]

        for idx, (metric, title) in enumerate(available):
            data = self.results.dropna(subset=[metric]).sort_values(metric)
            if data.empty:
                continue

            values = data[metric].astype(float)
            color = 'coral' if 'gini' in metric or 'gap' in metric else 'steelblue'
            axes[idx].bar(range(len(data)), values, color=color, alpha=0.8)
            axes[idx].set_xticks(range(len(data)))
            axes[idx].set_xticklabels(data['strategy'], rotation=45, ha='right', fontsize=8)
            axes[idx].set_title(title, fontsize=11)

            for i, v in enumerate(values):
                label = f'{v:,.0f}' if v > 100 else f'{v:.3f}'
                axes[idx].text(i, v, label, ha='center', va='bottom', fontsize=7)

        plt.suptitle('Equity Metrics by Strategy', fontsize=14, y=1.02)
        plt.tight_layout()
        self._save_fig('equity_comparison.png')

    def create_variant_timeline_plot(self) -> None:
        """Show variant emergence on the infection timeline."""
        if 'variant' not in self.time_series.columns:
            return

        fig, ax = plt.subplots(figsize=(15, 6))

        # Use first strategy's data for reference
        strategies = self.results['strategy'].unique()
        if len(strategies) == 0:
            return

        sdata = self.time_series[self.time_series['strategy'] == strategies[0]]
        if sdata.empty or 'infection_rate' not in sdata.columns:
            return

        ax.plot(sdata['day'], sdata['infection_rate'].astype(float),
               color='steelblue', alpha=0.8, label='Infection Rate (%)')

        # Mark variant transitions
        variants_seen = set()
        for _, row in sdata.iterrows():
            v = row['variant']
            if v not in variants_seen:
                variants_seen.add(v)
                ax.axvline(x=row['day'], color='gray', linestyle=':', alpha=0.5)
                ax.text(row['day'], ax.get_ylim()[1] * 0.9, f' {v}',
                       fontsize=9, rotation=90, va='top', color='darkred')

        ax.set_title('Variant Timeline with Infection Rate')
        ax.set_xlabel('Days')
        ax.set_ylabel('Infection Rate (%)')
        ax.legend()
        plt.tight_layout()
        self._save_fig('variant_timeline.png')

    def create_hospitalization_plot(self) -> None:
        """Hospitalization burden over time by strategy."""
        if 'total_hospitalized' not in self.time_series.columns:
            return

        fig, ax = plt.subplots(figsize=(15, 8))
        colors = plt.cm.tab10.colors
        strategies = self.results['strategy'].unique()

        for idx, strategy in enumerate(strategies):
            sdata = self.time_series[self.time_series['strategy'] == strategy]
            if not sdata.empty:
                ax.plot(sdata['day'],
                       sdata['total_hospitalized'].astype(float),
                       label=strategy, color=colors[idx % len(colors)], alpha=0.8)

        ax.set_title('Global Hospitalizations by Strategy')
        ax.set_xlabel('Days')
        ax.set_ylabel('Total Hospitalized')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        plt.tight_layout()
        self._save_fig('hospitalizations.png')

    def export_all_visualizations(self) -> None:
        """Generate all visualization plots."""
        try:
            print("  Generating metric comparison plot...")
            self.create_metric_comparison_plot()

            print("  Generating immunity progression timeline...")
            self.create_timeline_plot()

            print("  Generating cumulative deaths plot...")
            self.create_deaths_plot()

            print("  Generating equity comparison plot...")
            self.create_equity_comparison_plot()

            print("  Generating variant timeline plot...")
            self.create_variant_timeline_plot()

            print("  Generating hospitalization plot...")
            self.create_hospitalization_plot()

            print("  All visualizations generated successfully")

        except Exception as e:
            print(f"  Error during visualization: {e}")
            try:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, f"Error generating visualizations:\n{e}",
                        ha='center', va='center')
                plt.axis('off')
                self._save_fig('visualization_error.png')
            except Exception as inner_e:
                print(f"  Could not generate error visualization: {inner_e}")
