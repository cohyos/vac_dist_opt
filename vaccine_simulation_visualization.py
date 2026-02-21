"""Enhanced visualization suite for vaccination strategy simulation"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from typing import List, Dict, Union, Optional
from lockdown_controller import LockdownController

class VaccinationVisualizer:
    def __init__(self, results_df: pd.DataFrame, time_series_data: List[Dict], lockdown_controller: LockdownController):
        self.results = results_df.convert_dtypes()  # More robust way to handle data types
        self.time_series = pd.DataFrame(time_series_data).convert_dtypes()
        self.lockdown_controller = lockdown_controller
        
        plt.rcParams['figure.figsize'] = [12, 8]
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['font.size'] = 10
        plt.rcParams['lines.linewidth'] = 2

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
        plt.savefig('strategy_metrics_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

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
        plt.savefig('immunity_progression.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_lockdown_visualization(self) -> None:
        """Creates visualization showing infection rates and lockdown periods"""
        plt.figure(figsize=(15, 10))
        
        plt.plot(self.time_series['day'], 
                self.time_series['infection_rate'],
                label='Infection Rate', 
                color='blue', 
                linewidth=2)
        
        plt.axhline(y=self.lockdown_controller.entry_threshold * 100,
                    color='red',
                    linestyle='--',
                    label='Lockdown Entry Threshold')
        plt.axhline(y=self.lockdown_controller.exit_threshold * 100,
                    color='green',
                    linestyle='--',
                    label='Lockdown Exit Threshold')
        
        ymin, ymax = plt.ylim()
        for period in self.lockdown_controller.lockdown_periods:
            plt.axvspan(period['start'], 
                       period['end'],
                       alpha=0.2,
                       color='red',
                       label='Lockdown Period' if period == self.lockdown_controller.lockdown_periods[0] else "")
        
        stats = self.lockdown_controller.get_lockdown_statistics()
        plt.text(0.02, 0.98,
                 f"Total Lockdown Periods: {stats['total_periods']}\n"
                 f"Total Days in Lockdown: {stats['total_days']}\n"
                 f"Average Duration: {stats['average_duration']:.1f} days",
                 transform=plt.gca().transAxes,
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.title('Infection Rate and Lockdown Periods Over Time')
        plt.xlabel('Simulation Day')
        plt.ylabel('Infection Rate (%)')
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('lockdown_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

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
                plt.savefig('visualization_error.png')
                plt.close()
            except:
                print("Could not generate error visualization")