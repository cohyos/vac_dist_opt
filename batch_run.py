import os
print(os.getcwd())
os.chdir("D:\\Users\yoshefch\Phd files\sim\dec24_cld_strg")
print (os.getcwd())

from vaccine_simulation_config import generate_default_config

generate_default_config('simulation_config.yaml')


from covid_vaccine_simulation_main import run_complete_simulation
run_complete_simulation(
    config_path='simulation_config.yaml',
    countries_path='data/world_countries_data.csv',
    vaccines_path='data/daily_vaccine_availability.csv',
    output_dir='results'
)
