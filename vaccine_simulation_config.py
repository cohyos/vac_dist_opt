"""Configuration management for COVID-19 vaccination simulation"""

import yaml
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SimulationConfig:
    # Disease parameters
    basic_reproduction_number: float = 2.1
    recovery_rate: float = 1/14
    mortality_rate: float = 0.02
    vaccine_effectiveness: float = 0.95

    # Simulation parameters
    initial_infected_per_country: int = 100
    herd_immunity_threshold: float = 0.7
    lockdown_threshold: float = 0.012
    simulation_days: int = 800
    lockdown_entry_threshold: float = 0.012
    lockdown_exit_threshold: float = 0.008
    random_seed: int = 42

    # Economic parameters
    gdp_immunity_threshold: float = 0.7
    country_immunity_threshold: float = 0.5
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'SimulationConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_yaml(self, file_path: str) -> None:
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False)

def generate_default_config(file_path: str = 'simulation_config.yaml') -> None:
    """Generate default configuration file"""
    config = SimulationConfig()
    config.to_yaml(file_path)

class StrategyConfig:
    """Configuration for vaccine distribution strategies"""
    STRATEGIES = {
        'population_proportional': 'Proportional to Population',
        'large_population_first': 'Large Population First',
        'small_population_first': 'Small Population First',
        'high_gdp_first': 'High GDP First',
        'low_gdp_first': 'Low GDP First',
        'high_gni_first': 'High GNI per Capita First',
        'low_gni_first': 'Low GNI per Capita First'
    }
    
    @classmethod
    def get_strategy_name(cls, strategy_key: str) -> str:
        return cls.STRATEGIES.get(strategy_key, 'Unknown Strategy')
    
    @classmethod
    def get_all_strategies(cls) -> Dict[str, str]:
        return cls.STRATEGIES.copy()
