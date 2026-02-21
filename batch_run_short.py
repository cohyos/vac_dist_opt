
from covid_vaccine_simulation_main import run_complete_simulation
run_complete_simulation(
    config_path='simulation_config.yaml',
    countries_path='data/world_countries_data.csv',
    vaccines_path='data/daily_vaccine_availability.csv',
    output_dir='results'
)
