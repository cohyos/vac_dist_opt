"""Enhanced visualization suite for vaccination strategy simulation"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import json
from typing import List, Dict, Union, Optional
from lockdown_controller import LockdownController


class VaccinationVisualizer:
    def __init__(self, results_df: pd.DataFrame, time_series_data: List[Dict],
                 lockdown_controllers: Dict[str, LockdownController],
                 output_dir: str = 'results'):
        self.results = results_df.convert_dtypes()
        self.time_series = pd.DataFrame(time_series_data).convert_dtypes()
        self.lockdown_controllers = lockdown_controllers
        self.output_dir = output_dir

        plt.rcParams['figure.figsize'] = [12, 8]
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['font.size'] = 10
        plt.rcParams['lines.linewidth'] = 2

    def _save_fig(self, filename: str) -> None:
        """Save figure to the output directory."""
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()

    def create_metric_comparison_plot(self) -> None:
        metrics = ['days_to_70_global', 'days_to_70_economic',
                  'days_to_50_countries', 'total_deaths']

        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        axes = axes.ravel()

        for idx, metric in enumerate(metrics):
            if metric not in self.results.columns:
                continue

            data = self.results.sort_values(metric)
            values = data[metric].astype(float)

            axes[idx].bar(range(len(data)), values, color='skyblue')
            axes[idx].set_xticks(range(len(data)))
            axes[idx].set_xticklabels(data['strategy'], rotation=45, ha='right')
            axes[idx].set_title(metric.replace('_', ' ').title())
            axes[idx].grid(True, alpha=0.3)

            for i, v in enumerate(values):
                if pd.notna(v):
                    axes[idx].text(i, v, f'{v:.1f}', ha='center', va='bottom')

        plt.tight_layout()
        self._save_fig('strategy_metrics_comparison.png')

    def create_timeline_plot(self) -> None:
        fig, ax = plt.subplots(figsize=(15, 8))

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

        for idx, strategy in enumerate(self.results['strategy'].unique()):
            strategy_data = self.time_series[self.time_series['strategy'] == strategy]
            if 'global_immunity_percentage' in strategy_data.columns:
                ax.plot(
                    strategy_data['day'],
                    strategy_data['global_immunity_percentage'].astype(float),
                    label=strategy,
                    color=colors[idx % len(colors)]
                )

        ax.axhline(y=70, color='red', linestyle='--', label='Immunity Threshold')
        ax.set_title('Global Immunity Progression by Strategy')
        ax.set_xlabel('Days')
        ax.set_ylabel('Global Immunity Percentage')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save_fig('immunity_progression.png')

    def create_lockdown_visualization(self) -> None:
        """Creates visualization showing infection rates and lockdown periods per strategy"""
        n_strategies = len(self.lockdown_controllers)
        if n_strategies == 0:
            print("No lockdown data available for visualization")
            return

        fig, axes = plt.subplots(n_strategies, 1, figsize=(15, 5 * n_strategies), squeeze=False)

        for idx, (strategy_name, controller) in enumerate(self.lockdown_controllers.items()):
            ax = axes[idx, 0]

            # Plot infection rate for this strategy
            strategy_data = self.time_series[self.time_series['strategy'] == strategy_name]
            if 'infection_rate' in strategy_data.columns and not strategy_data.empty:
                ax.plot(strategy_data['day'],
                       strategy_data['infection_rate'].astype(float),
                       label='Infection Rate (%)',
                       color='blue',
                       linewidth=1.5)

            ax.axhline(y=controller.entry_threshold * 100,
                      color='red', linestyle='--', alpha=0.7,
                      label='Lockdown Entry Threshold')
            ax.axhline(y=controller.exit_threshold * 100,
                      color='green', linestyle='--', alpha=0.7,
                      label='Lockdown Exit Threshold')

            for period in controller.lockdown_periods:
                ax.axvspan(period['start'], period['end'],
                          alpha=0.15, color='red',
                          label='Lockdown' if period == controller.lockdown_periods[0] else "")

            stats = controller.get_lockdown_statistics()
            ax.text(0.02, 0.98,
                    f"Lockdowns: {stats['total_periods']} | "
                    f"Total Days: {stats['total_days']} | "
                    f"Avg Duration: {stats['average_duration']:.1f}d",
                    transform=ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    fontsize=9)

            ax.set_title(f'{strategy_name}')
            ax.set_xlabel('Simulation Day')
            ax.set_ylabel('Infection Rate (%)')
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, alpha=0.3)

        plt.suptitle('Infection Rate and Lockdown Periods by Strategy', fontsize=14, y=1.01)
        plt.tight_layout()
        self._save_fig('lockdown_analysis.png')

    def export_all_visualizations(self) -> None:
        try:
            print("Generating metric comparison plot...")
            self.create_metric_comparison_plot()

            print("Generating immunity progression timeline...")
            self.create_timeline_plot()

            print("Generating lockdown analysis visualization...")
            self.create_lockdown_visualization()

            print("All visualizations generated successfully")

        except Exception as e:
            print(f"Error during visualization generation: {str(e)}")
            try:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, f"Error generating visualizations:\n{str(e)}",
                        ha='center', va='center')
                plt.axis('off')
                self._save_fig('visualization_error.png')
            except Exception as inner_e:
                print(f"Could not generate error visualization: {inner_e}")
