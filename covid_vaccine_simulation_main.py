"""
Main simulation runner for COVID-19 vaccination strategy analysis
Integrates configuration, analysis, and visualization components with improved error handling
"""

import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Import from companion modules
from vaccine_simulation_config import SimulationConfig, StrategyConfig
from vaccine_simulation_analysis import VaccinationAnalyzer
from vaccine_simulation_visualization import VaccinationVisualizer
from lockdown_controller import LockdownController



class Country:
    def __init__(self, name: str, population: int, gni_per_capita: float, 
                 config: SimulationConfig, initial_infected: int = None):
        self.name = name
        self.population = population
        self.gni_per_capita = gni_per_capita
        self.gdp = population * gni_per_capita
        
        # Set initial infected based on config or default
        self.initial_infected = initial_infected or config.initial_infected_per_country
        
        # Disease states
        self.susceptible = population - self.initial_infected
        self.infected = self.initial_infected
        self.recovered = 0
        self.vaccinated = 0
        self.deaths = 0
        
        # Disease parameters from config
        self.R0 = config.basic_reproduction_number
        self.recovery_rate = config.recovery_rate
        self.mortality_rate = config.mortality_rate
        self.vaccine_effectiveness = config.vaccine_effectiveness
        
        # Immunity tracking
        self.has_reached_immunity = False
        self.day_reached_immunity = None
        self.immunity_threshold = config.herd_immunity_threshold
    
    def get_immunity_percentage(self) -> float:
        """Calculate current immunity percentage"""
        total_immune = self.recovered + (self.vaccinated * self.vaccine_effectiveness)
        return (total_immune / self.population) * 100
    
    def update(self, day: int, global_lockdown: bool) -> Dict:
        """Update disease progression with improved error handling"""
        # Calculate basic parameters
        current_R0 = self.R0 * (0.4 if global_lockdown else 1.0)
        effective_r0 = current_R0 * (self.susceptible / max(1, self.population))
        infection_rate = effective_r0 * self.recovery_rate
        
        # Ensure non-negative values for all compartments
        self.susceptible = max(0, self.susceptible)
        self.infected = max(0, self.infected)
        self.recovered = max(0, self.recovered)
        self.vaccinated = max(0, self.vaccinated)
        
        # Calculate new infections
        new_infections = np.random.poisson(infection_rate * self.infected)
        new_infections = min(new_infections, self.susceptible)
        
        # Calculate recoveries and deaths with proper bounds
        current_infected = int(max(0, self.infected))  # Convert to int for binomial
        new_recoveries = np.random.binomial(current_infected, self.recovery_rate)
        new_deaths = np.random.binomial(new_recoveries, self.mortality_rate)
        new_recoveries = max(0, new_recoveries - new_deaths)
        
        # Update compartments with bounds checking
        self.susceptible = max(0, self.susceptible - new_infections)
        self.infected = max(0, self.infected + new_infections - new_recoveries - new_deaths)
        self.recovered += new_recoveries
        self.deaths += new_deaths
        self.population = max(0, self.population - new_deaths)
        
        # Check immunity threshold
        immunity_reached = False
        if not self.has_reached_immunity and self.get_immunity_percentage() >= (self.immunity_threshold * 100):
            self.has_reached_immunity = True
            self.day_reached_immunity = day
            immunity_reached = True
        
        return {
            'new_infections': new_infections,
            'new_deaths': new_deaths,
            'reached_immunity': immunity_reached
        }

class VaccineDistributor:
    """Handles vaccine distribution according to different strategies"""
    
    @staticmethod
    def population_proportional(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        total_population = sum(country.population for country in countries.values())
        return {name: int(available_vaccines * (country.population / total_population))
                for name, country in countries.items()}
    
    @staticmethod
    def large_population_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].population, reverse=True)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def small_population_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].population)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def high_gdp_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gdp, reverse=True)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def low_gdp_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gdp)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def high_gni_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gni_per_capita, reverse=True)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def low_gni_first(countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gni_per_capita)
        return VaccineDistributor._allocate_sequentially(sorted_countries, available_vaccines)
    
    @staticmethod
    def _allocate_sequentially(sorted_countries: List[Tuple[str, Country]],
                             available_vaccines: int,
                             daily_cap_fraction: float = 0.005) -> Dict[str, int]:
        """Allocate vaccines sequentially with per-country daily absorption cap.

        Each country can absorb at most daily_cap_fraction of its population per day,
        preventing unrealistic scenarios where one large country absorbs all vaccines.
        """
        allocations = {name: 0 for name, _ in sorted_countries}
        remaining_vaccines = max(0, available_vaccines)

        # Multiple passes to distribute remaining vaccines after caps
        while remaining_vaccines > 0:
            distributed_this_pass = 0
            for name, country in sorted_countries:
                if remaining_vaccines <= 0:
                    break
                max_daily = max(1, int(country.population * daily_cap_fraction))
                already_allocated = allocations[name]
                can_absorb = max(0, max_daily - already_allocated)
                needed = min(country.susceptible - already_allocated, remaining_vaccines, can_absorb)
                if needed > 0:
                    allocations[name] += needed
                    remaining_vaccines -= needed
                    distributed_this_pass += needed
            if distributed_this_pass == 0:
                break  # No country can absorb more vaccines

        return allocations

class GlobalSimulation:
    def __init__(self, config_path: str):
        self.config = SimulationConfig.from_yaml(config_path)
        self.strategy_mapping = {
            'population_proportional': VaccineDistributor.population_proportional,
            'large_population_first': VaccineDistributor.large_population_first,
            'small_population_first': VaccineDistributor.small_population_first,
            'high_gdp_first': VaccineDistributor.high_gdp_first,
            'low_gdp_first': VaccineDistributor.low_gdp_first,
            'high_gni_first': VaccineDistributor.high_gni_first,
            'low_gni_first': VaccineDistributor.low_gni_first
        }
        # Store per-strategy lockdown controllers for visualization
        self.lockdown_controllers = {}
        self.num_countries = 0
    
    def _run_single_strategy(self, countries_data: pd.DataFrame,
                           vaccines_data: pd.DataFrame,
                           strategy_func, strategy_name: str) -> Tuple[Dict, List[Dict]]:
        try:
            countries = {
                row['Country']: Country(
                    row['Country'], row['Population'], row['GNI_per_capita'],
                    self.config
                )
                for _, row in countries_data.iterrows()
            }
        except Exception as e:
            raise RuntimeError(f"Failed to initialize countries: {str(e)}")

        self.num_countries = len(countries)
        time_series = []
        simulation_days = min(self.config.simulation_days, len(vaccines_data))

        # Create a fresh lockdown controller for this strategy
        lockdown_controller = LockdownController(
            entry_threshold=self.config.lockdown_entry_threshold,
            exit_threshold=self.config.lockdown_exit_threshold
        )
        
        for day in tqdm(range(simulation_days)):
            try:
                available_vaccines = max(0, vaccines_data.iloc[day]['available_vaccines'])
                allocations = strategy_func(countries, available_vaccines)
                
                for name, vaccines in allocations.items():
                    countries[name].vaccinated += vaccines
                    countries[name].susceptible = max(0, countries[name].susceptible - vaccines)
                
                # Update lockdown status
                total_population = sum(c.population for c in countries.values())
                total_infected = sum(c.infected for c in countries.values())
                infection_rate = total_infected / total_population if total_population > 0 else 0
                global_lockdown = lockdown_controller.update_lockdown_status(day, infection_rate)
                
                # Update disease progression with lockdown status
                for country in countries.values():
                    country.update(day, global_lockdown)
                
                stats = self._calculate_global_stats(countries, day, strategy_name)
                time_series.append(stats)
                
            except Exception as e:
                print(f"Warning: Error on day {day}: {str(e)}")
                continue
        
        # Store this strategy's lockdown controller for visualization
        self.lockdown_controllers[strategy_name] = lockdown_controller

        final_stats = self._analyze_strategy_results(time_series, strategy_name)
        return final_stats, time_series
	    
    def run_simulation(self, countries_data: pd.DataFrame, vaccines_data: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Runs simulation for all strategies and returns aggregate results
        
        Args:
            countries_data: DataFrame containing country information
            vaccines_data: DataFrame containing vaccine availability data
        
        Returns:
            Tuple containing:
                - DataFrame with results for each strategy
                - List of time series dictionaries for visualization
        """
        # Set random seed for reproducibility
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

        results = []
        time_series_data = []

        for strategy_key, strategy_func in self.strategy_mapping.items():
            print(f"\nRunning simulation with {strategy_key} strategy...")
            try:
                strategy_result, strategy_timeseries = self._run_single_strategy(
                    countries_data, 
                    vaccines_data, 
                    strategy_func, 
                    strategy_key
                )
                results.append(strategy_result)
                time_series_data.extend(strategy_timeseries)
                
                # Log strategy completion
                print(f"Completed {strategy_key} strategy simulation")
                if strategy_result['total_deaths'] > 0:
                    print(f"Strategy resulted in {strategy_result['total_deaths']:,.0f} total deaths")
                
            except Exception as e:
                print(f"Error during {strategy_key} simulation: {str(e)}")
                continue
        
        if not results:
            raise RuntimeError("All simulation strategies failed to complete.")
        
        return pd.DataFrame(results), time_series_data

    def _calculate_global_stats(self, countries: Dict, day: int, strategy: str) -> Dict:
        """Calculate global statistics with error handling"""
        try:
            total_population = max(1, sum(c.population for c in countries.values()))
            total_gdp = max(1, sum(c.gdp for c in countries.values()))
            
            global_immunity = sum(c.get_immunity_percentage() * c.population 
                                for c in countries.values()) / total_population
            economic_immunity = sum(c.get_immunity_percentage() * c.gdp 
                                  for c in countries.values()) / total_gdp
            
            total_infected = sum(c.infected for c in countries.values())

            return {
                'day': day,
                'strategy': strategy,
                'global_immunity_percentage': global_immunity,
                'economic_immunity_percentage': economic_immunity,
                'countries_with_immunity': sum(1 for c in countries.values()
                                             if c.get_immunity_percentage() >= (self.config.herd_immunity_threshold * 100)),
                'total_deaths': sum(c.deaths for c in countries.values()),
                'infection_rate': (total_infected / total_population) * 100
            }
        except Exception as e:
            print(f"Warning: Error calculating global stats: {str(e)}")
            return {
                'day': day,
                'strategy': strategy,
                'global_immunity_percentage': 0,
                'economic_immunity_percentage': 0,
                'countries_with_immunity': 0,
                'total_deaths': 0,
                'infection_rate': 0
            }
    
    def _analyze_strategy_results(self, time_series: List[Dict], strategy: str) -> Dict:
        """Analyze strategy results with error handling"""
        try:
            df = pd.DataFrame(time_series)
            
            immunity_threshold = self.config.herd_immunity_threshold * 100
            country_threshold = self.config.country_immunity_threshold * self.num_countries
            
            days_to_70_global = None
            if (df['global_immunity_percentage'] >= immunity_threshold).any():
                days_to_70_global = df[df['global_immunity_percentage'] >= immunity_threshold].iloc[0]['day']
            
            days_to_70_economic = None
            if (df['economic_immunity_percentage'] >= immunity_threshold).any():
                days_to_70_economic = df[df['economic_immunity_percentage'] >= immunity_threshold].iloc[0]['day']
            
            days_to_50_countries = None
            if (df['countries_with_immunity'] >= country_threshold).any():
                days_to_50_countries = df[df['countries_with_immunity'] >= country_threshold].iloc[0]['day']
            
            return {
                'strategy': strategy,
                'days_to_70_global': days_to_70_global,
                'days_to_70_economic': days_to_70_economic,
                'days_to_50_countries': days_to_50_countries,
                'total_deaths': df.iloc[-1]['total_deaths']
            }
        except Exception as e:
            print(f"Warning: Error analyzing results: {str(e)}")
            return {
                'strategy': strategy,
                'days_to_70_global': None,
                'days_to_70_economic': None,
                'days_to_50_countries': None,
                'total_deaths': 0
            }

def run_complete_simulation(config_path: str, 
                          countries_path: str,
                          vaccines_path: str,
                          output_dir: str = 'results') -> None:
    """Run complete simulation with analysis and visualization"""
    try:
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load data
        print("Loading data files...")
        countries_data = pd.read_csv(countries_path)
        vaccines_data = pd.read_csv(vaccines_path)
        
        # Run simulation
        print("Initializing simulation...")
        simulation = GlobalSimulation(config_path)
        
        print("Running simulation strategies...")
        results, time_series = simulation.run_simulation(countries_data, vaccines_data)
        
        # Save raw results
        print("Saving simulation results...")
        results.to_csv(f"{output_dir}/simulation_results.csv", index=False)
        pd.DataFrame(time_series).to_csv(f"{output_dir}/time_series_data.csv", index=False)
        
        # Run analysis
        print("Analyzing results...")
        analyzer = VaccinationAnalyzer(results)
        analyzer.export_analysis(output_dir)
        
        # Create visualizations
        print("Generating visualizations...")
        visualizer = VaccinationVisualizer(
            results, time_series, simulation.lockdown_controllers, output_dir
        )
        visualizer.export_all_visualizations()

        print("\nSimulation completed successfully!")
        print(f"All results have been saved to: {output_dir}/")

    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='COVID-19 Vaccine Distribution Simulation')
    parser.add_argument('--config', default='simulation_config.yaml', help='Path to config YAML')
    parser.add_argument('--countries', default='data/world_countries_data.csv', help='Path to countries CSV')
    parser.add_argument('--vaccines', default='data/daily_vaccine_availability.csv', help='Path to vaccines CSV')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    args = parser.parse_args()

    run_complete_simulation(
        config_path=args.config,
        countries_path=args.countries,
        vaccines_path=args.vaccines,
        output_dir=args.output_dir
    )
