import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import Dict, List, Tuple
import seaborn as sns

class VaccinationStrategy:
    """Base class for vaccination strategies"""
    def __init__(self, name: str):
        self.name = name
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        raise NotImplementedError

class PopulationProportionalStrategy(VaccinationStrategy):
    def __init__(self):
        super().__init__("Population Proportional")
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        total_population = sum(country.population for country in countries.values())
        allocations = {}
        for name, country in countries.items():
            country_share = int(available_vaccines * (country.population / total_population))
            allocations[name] = country_share
        return allocations

class LargePopulationFirstStrategy(VaccinationStrategy):
    def __init__(self):
        super().__init__("Large Population First")
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].population, reverse=True)
        return self._allocate_sequentially(sorted_countries, available_vaccines)

class SmallPopulationFirstStrategy(VaccinationStrategy):
    def __init__(self):
        super().__init__("Small Population First")
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].population)
        return self._allocate_sequentially(sorted_countries, available_vaccines)

class HighGNIFirstStrategy(VaccinationStrategy):
    def __init__(self):
        super().__init__("High GNI First")
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gni_per_capita, reverse=True)
        return self._allocate_sequentially(sorted_countries, available_vaccines)

class LowGNIFirstStrategy(VaccinationStrategy):
    def __init__(self):
        super().__init__("Low GNI First")
    
    def allocate_vaccines(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        sorted_countries = sorted(countries.items(), key=lambda x: x[1].gni_per_capita)
        return self._allocate_sequentially(sorted_countries, available_vaccines)

    @staticmethod
    def _allocate_sequentially(sorted_countries: List[Tuple[str, 'Country']], available_vaccines: int) -> Dict[str, int]:
        allocations = {name: 0 for name, _ in sorted_countries}
        remaining_vaccines = available_vaccines
        
        for name, country in sorted_countries:
            if remaining_vaccines <= 0:
                break
            needed = min(country.susceptible, remaining_vaccines)
            allocations[name] = needed
            remaining_vaccines -= needed
        
        return allocations

class Country:
    def __init__(self, name: str, population: int, gni_per_capita: float, initial_infected: int = 100):
        self.name = name
        self.population = population
        self.gni_per_capita = gni_per_capita
        self.gdp = population * gni_per_capita
        
        # Disease states
        self.susceptible = population - initial_infected
        self.infected = initial_infected
        self.recovered = 0
        self.vaccinated = 0
        self.deaths = 0
        
        # Health system capacity based on GNI
        self.healthcare_capacity = self._calculate_healthcare_capacity()
        
        # Disease parameters
        self.base_R0 = 2.1
        self.current_R0 = 2.1
        self.recovery_rate = 1/14
        self.vaccine_effectiveness = 0.95
        
        # Immunity tracking
        self.has_reached_immunity = False
        self.day_reached_immunity = None
    
    def _calculate_healthcare_capacity(self) -> float:
        """Calculate healthcare capacity based on GNI per capita"""
        base_capacity = 0.001  # Base capacity per capita
        gni_factor = np.log(self.gni_per_capita / 1000 + 1)
        return self.population * base_capacity * (1 + gni_factor)
    
    def calculate_mortality_rate(self) -> float:
        """Calculate mortality rate based on healthcare system load"""
        base_rate = 0.02
        healthcare_load = self.infected / self.healthcare_capacity
        return base_rate * (1 + max(0, healthcare_load - 1))
    
    def get_immunity_percentage(self) -> float:
        """Calculate current immunity percentage"""
        total_immune = self.recovered + (self.vaccinated * self.vaccine_effectiveness)
        return (total_immune / self.population) * 100
    
    def update(self, day: int, global_lockdown: bool) -> Dict:
        self.current_R0 = self.base_R0 * (0.4 if global_lockdown else 1.0)
        
        effective_r0 = self.current_R0 * (self.susceptible / self.population)
        infection_rate = effective_r0 * self.recovery_rate
        
        new_infections = np.random.poisson(infection_rate * self.infected)
        new_infections = min(new_infections, self.susceptible)
        
        mortality_rate = self.calculate_mortality_rate()
        new_recoveries = np.random.binomial(self.infected, self.recovery_rate)
        new_deaths = np.random.binomial(new_recoveries, mortality_rate)
        new_recoveries -= new_deaths
        
        self.susceptible -= new_infections
        self.infected += (new_infections - new_recoveries - new_deaths)
        self.recovered += new_recoveries
        self.deaths += new_deaths
        
        # Update immunity status
        if not self.has_reached_immunity and self.get_immunity_percentage() >= 70:
            self.has_reached_immunity = True
            self.day_reached_immunity = day
        
        return {
            'new_infections': new_infections,
            'new_recoveries': new_recoveries,
            'new_deaths': new_deaths
        }

class GlobalSimulation:
    def __init__(self, countries_data: pd.DataFrame, vaccines_data: pd.DataFrame):
        self.countries = {
            row['Country']: Country(row['Country'], row['Population'], row['GNI_per_capita'])
            for _, row in countries_data.iterrows()
        }
        self.vaccines_data = vaccines_data
        self.strategies = [
            PopulationProportionalStrategy(),
            LargePopulationFirstStrategy(),
            SmallPopulationFirstStrategy(),
            HighGNIFirstStrategy(),
            LowGNIFirstStrategy()
        ]
    
    def run_all_strategies(self) -> pd.DataFrame:
        results = []
        for strategy in self.strategies:
            print(f"\nRunning simulation with {strategy.name} strategy...")
            strategy_results = self.run_single_strategy(strategy)
            results.append(strategy_results)
        
        return pd.DataFrame(results)
    
    def run_single_strategy(self, strategy: VaccinationStrategy) -> Dict:
        simulation_days = len(self.vaccines_data)
        global_stats = []
        global_lockdown = False
        
        # Reset countries for new simulation
        self.reset_countries()
        
        for day in tqdm(range(simulation_days)):
            available_vaccines = self.vaccines_data.iloc[day]['available_vaccines']
            
            # Allocate vaccines according to strategy
            allocations = strategy.allocate_vaccines(self.countries, available_vaccines)
            for name, vaccines in allocations.items():
                self.countries[name].vaccinated += vaccines
                self.countries[name].susceptible -= vaccines
            
            # Update infection status
            self._update_all_countries(day, global_lockdown)
            
            # Calculate global statistics
            stats = self._calculate_global_stats(day)
            global_stats.append(stats)
            
            # Update lockdown status
            global_lockdown = self._should_enforce_lockdown(stats['global_infection_rate'])
        
        return self._analyze_strategy_results(strategy.name, global_stats)
    
    def _update_all_countries(self, day: int, global_lockdown: bool) -> None:
        for country in self.countries.values():
            country.update(day, global_lockdown)
    
    def _calculate_global_stats(self, day: int) -> Dict:
        total_population = sum(c.population for c in self.countries.values())
        total_gdp = sum(c.gdp for c in self.countries.values())
        
        stats = {
            'day': day,
            'global_immunity_percentage': sum(c.get_immunity_percentage() * c.population 
                                           for c in self.countries.values()) / total_population,
            'economic_immunity_percentage': sum(c.get_immunity_percentage() * c.gdp 
                                            for c in self.countries.values()) / total_gdp,
            'countries_with_immunity': sum(1 for c in self.countries.values() 
                                        if c.get_immunity_percentage() >= 70),
            'total_deaths': sum(c.deaths for c in self.countries.values()),
            'global_infection_rate': sum(c.infected for c in self.countries.values()) / total_population
        }
        
        return stats
    
    def _analyze_strategy_results(self, strategy_name: str, global_stats: List[Dict]) -> Dict:
        stats_df = pd.DataFrame(global_stats)
        
        days_to_70_global = None
        days_to_70_economic = None
        days_to_50_countries = None
        
        if (stats_df['global_immunity_percentage'] >= 70).any():
            days_to_70_global = stats_df[stats_df['global_immunity_percentage'] >= 70].iloc[0]['day']
        
        if (stats_df['economic_immunity_percentage'] >= 70).any():
            days_to_70_economic = stats_df[stats_df['economic_immunity_percentage'] >= 70].iloc[0]['day']
        
        num_countries = len(self.countries)
        if (stats_df['countries_with_immunity'] >= num_countries * 0.5).any():
            days_to_50_countries = stats_df[stats_df['countries_with_immunity'] >= num_countries * 0.5].iloc[0]['day']
        
        return {
            'strategy': strategy_name,
            'days_to_70_global': days_to_70_global,
            'days_to_70_economic': days_to_70_economic,
            'days_to_50_countries': days_to_50_countries,
            'total_deaths': stats_df.iloc[-1]['total_deaths']
        }
    
    def reset_countries(self) -> None:
        """Reset all countries to initial state for new simulation"""
        countries_data = pd.DataFrame([{
            'Country': c.name,
            'Population': c.population,
            'GNI_per_capita': c.gni_per_capita
        } for c in self.countries.values()])
        
        self.countries = {
            row['Country']: Country(row['Country'], row['Population'], row['GNI_per_capita'])
            for _, row in countries_data.iterrows()
        }
    
    @staticmethod
    def _should_enforce_lockdown(infection_rate: float) -> bool:
        return infection_rate >= 0.01  # 1% threshold for lockdown

def plot_results(results: pd.DataFrame) -> None:
    """Create visualization of simulation results"""
    plt.style.use('seaborn')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Days to 70% global immunity
    sns.barplot(x='strategy', y='days_to_70_global', data=results, ax=ax1)
    ax1.set_title('Days to 70% Global Immunity')
    ax1.tick_params(axis='x', rotation=45)
    
    # Days to 70% economic immunity
    sns.barplot(x='strategy', y='days_to_70_economic', data=results, ax=ax2)
    ax2.set_title('Days to 70% Economic Immunity')
    ax2.tick_params(axis='x', rotation=45)
    
    # Days to 50% countries immunity
    sns.barplot(x='strategy', y='days_to_50_countries', data=results, ax=ax3)
    ax3.set_title('Days to 50% Countries Immunity')
    ax3.tick_params(axis='x', rotation=45)
    
    # Total deaths
    sns.barplot(x='strategy', y='total_deaths', data=results, ax=ax4)
    ax4.set_title('Total Deaths')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('strategy_comparison_results.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load data
    countries_data = pd.read_csv('world_countries_data.csv')
    vaccines_data = pd.read_csv('weekly_vaccine_availability.csv')
    
    # Run simulation
    simulation = GlobalSimulation(countries_data, vaccines_data)
    results = simulation.run_all_strategies()
    
    # Plot and save results
    plot_results(results)
    results.to_csv('vaccination_strategy_results.csv', index=False)
    
    print("\nSimulation Results:")
    print("=" * 80)
    print(results.to_string())
    print("\nResults have been saved to 'vaccination_strategy_results.csv'")
    print("Visualizations have been saved to 'strategy_comparison_results.png'")

if __name__ == "__main__":
    main()
