"""Batch runner for COVID-19 vaccine distribution simulation."""

import os
import sys

# Ensure we're in the correct directory (script's location)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from vaccine_simulation_config import generate_default_config

# Generate default config if it doesn't exist
if not os.path.exists('simulation_config.yaml'):
    generate_default_config('simulation_config.yaml')

from covid_vaccine_simulation_main import run_complete_simulation
run_complete_simulation(
    config_path='simulation_config.yaml',
    countries_path='data/world_countries_data.csv',
    vaccines_path='data/daily_vaccine_availability.csv',
    output_dir='results'
)
