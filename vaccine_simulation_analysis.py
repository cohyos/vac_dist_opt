"""Statistical analysis module for vaccination strategy simulation results"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import seaborn as sns
import matplotlib.pyplot as plt

class VaccinationAnalyzer:
    """Analyzes vaccination simulation results with improved error handling"""
    def __init__(self, results_df: pd.DataFrame):
        self.results = results_df
        self.metrics = ['days_to_70_global', 'days_to_70_economic', 
                       'days_to_50_countries', 'total_deaths']
    
    def perform_statistical_analysis(self) -> Dict:
        """Perform statistical analysis with proper error handling"""
        if self.results.empty:
            raise ValueError("Results DataFrame is empty")
            
        analysis = {
            'baseline_strategy': 'population_proportional',
            'metric_comparisons': {},
            'rankings': {},
            'summary_statistics': {}
        }
        
        # Get baseline strategy results
        baseline = self.results[self.results['strategy'] == 'population_proportional']
        if baseline.empty:
            # If population_proportional not found, use first strategy as baseline
            baseline = self.results.iloc[[0]]
            analysis['baseline_strategy'] = baseline['strategy'].iloc[0]
        
        # Calculate comparisons for each metric
        for metric in self.metrics:
            if metric not in self.results.columns:
                continue
                
            baseline_value = baseline[metric].iloc[0]
            if pd.isna(baseline_value):
                baseline_value = 0
                
            comparisons = {}
            for strategy in self.results['strategy'].unique():
                strategy_value = self.results[self.results['strategy'] == strategy][metric].iloc[0]
                if pd.isna(strategy_value):
                    strategy_value = 0
                
                if metric == 'total_deaths':
                    # For deaths, lower is better
                    improvement = ((baseline_value - strategy_value) / baseline_value * 100 
                                 if baseline_value != 0 else 0)
                else:
                    # For other metrics (days to reach targets), lower is better
                    improvement = ((baseline_value - strategy_value) / baseline_value * 100 
                                 if baseline_value != 0 else 0)
                
                comparisons[strategy] = {
                    'value': float(strategy_value),
                    'improvement': float(improvement)
                }
            
            analysis['metric_comparisons'][metric] = comparisons
            
            # Calculate rankings
            valid_values = self.results[~self.results[metric].isna()][metric]
            if not valid_values.empty:
                if metric == 'total_deaths':
                    rankings = valid_values.sort_values().index
                else:
                    rankings = valid_values.sort_values().index
                analysis['rankings'][metric] = list(self.results.loc[rankings, 'strategy'])
        
        # Calculate summary statistics
        for metric in self.metrics:
            if metric not in self.results.columns:
                continue
                
            valid_values = self.results[~self.results[metric].isna()][metric]
            if not valid_values.empty:
                analysis['summary_statistics'][metric] = {
                    'mean': float(valid_values.mean()),
                    'median': float(valid_values.median()),
                    'std': float(valid_values.std()) if len(valid_values) > 1 else 0,
                    'min': float(valid_values.min()),
                    'max': float(valid_values.max())
                }
        
        return analysis
    
    def export_analysis(self, output_dir: str) -> None:
        """Export analysis results with error handling"""
        try:
            analysis = self.perform_statistical_analysis()
            
            # Save detailed analysis to JSON
            with open(f"{output_dir}/analysis_results.json", 'w') as f:
                json.dump(analysis, f, indent=4)
            
            # Create summary report
            with open(f"{output_dir}/analysis_summary.txt", 'w') as f:
                f.write("Vaccination Strategy Analysis Summary\n")
                f.write("===================================\n\n")
                
                f.write(f"Baseline Strategy: {analysis['baseline_strategy']}\n\n")
                
                for metric in self.metrics:
                    if metric in analysis['rankings']:
                        f.write(f"\n{metric.replace('_', ' ').title()}:\n")
                        f.write("-" * (len(metric) + 1) + "\n")
                        
                        f.write("Rankings (Best to Worst):\n")
                        for i, strategy in enumerate(analysis['rankings'][metric], 1):
                            value = analysis['metric_comparisons'][metric][strategy]['value']
                            improvement = analysis['metric_comparisons'][metric][strategy]['improvement']
                            f.write(f"{i}. {strategy}: {value:.1f} ")
                            f.write(f"({improvement:+.1f}% vs baseline)\n")
                        
                        if metric in analysis['summary_statistics']:
                            stats = analysis['summary_statistics'][metric]
                            f.write(f"\nSummary Statistics:\n")
                            f.write(f"Mean: {stats['mean']:.1f}\n")
                            f.write(f"Median: {stats['median']:.1f}\n")
                            f.write(f"Std Dev: {stats['std']:.1f}\n")
                            f.write(f"Range: {stats['min']:.1f} - {stats['max']:.1f}\n")
                        
                        f.write("\n")
                
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            # Create minimal analysis file with error information
            with open(f"{output_dir}/analysis_error.txt", 'w') as f:
                f.write(f"Error occurred during analysis: {str(e)}\n")
                f.write("\nPartial Results:\n")
                f.write(str(self.results))
