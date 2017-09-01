import orca
import shutil
import sys
import os

import models, utils
from urbansim.utils import misc, networks
import output_indicators

data_out = utils.get_run_filename()
run_log = '.'.join(data_out.split('.')[:-1] + ['log'])

print('***The Standard stream is being written to {}***'.format(run_log))
sys.stdout = sys.stderr = open(run_log, 'w')

orca.run(['build_networks',
          "neighborhood_vars",
          "nrh_simulate",  # non-residential rent hedonic
          "rsh_simulate",  # residential sales hedonic
          ])

large_area_ids = [5, 3, 125, 99, 161, 115, 147, 93]

orca.run([
    "neighborhood_vars",
    "households_transition",
    "fix_lpr",
    "households_relocation",
    "jobs_transition",
    "jobs_relocation",
    "scheduled_demolition_events",
    "scheduled_development_events",
    "feasibility",
    "set_target_vacancies",
    "residential_developer",
    "non_residential_developer",
    "nrh_simulate",  # non-residential rent hedonic
    "rsh_simulate",  # residential sales hedonic
    "hlcm_simulate",  # households location choice
    "elcm_simulate",  # employment location choice
    "government_jobs_scaling_model",
    "refiner",
    # "gq_model", Fixme: we have new data so need new approach
    # "travel_model", Fixme: on hold
    # "housing_value_update", Fixme: maybe we don't need
],
    iter_vars=range(2016, 2045 + 1),
    # iter_vars=range(2016, 2016 + 5 + 1),
    data_out=data_out,
    out_base_tables=['jobs', 'employment_sectors', 'annual_relocation_rates_for_jobs',
                     'households', 'persons', 'annual_relocation_rates_for_households',
                     'buildings', 'parcels', 'zones', 'semmcds', 'counties',
                     'target_vacancies', 'building_sqft_per_job',
                     'annual_employment_control_totals',
                     'travel_data', 'zoning', 'large_areas', 'building_types', 'land_use_types',
                     'workers_labor_participation_rates', 'workers_employment_rates_by_large_area_age',
                     'workers_employment_rates_by_large_area',
                     'transit_stops', 'crime_rates', 'schools', 'poi',
                     'annual_household_control_totals',
                     'events_addition', 'events_deletion', 'refiner_events'],
    out_run_tables=(['buildings', 'jobs', 'parcels', 'households', 'persons',
                     'dropped_buildings', 'feasibility']
                    + ['feasibility_{}'.format(n) for n in large_area_ids]),
    out_interval=1,
    compress=True)

output_indicators.main(data_out)

# dir_out = data_out.replace('.h5', '')
# shutil.copytree(dir_out, '/mnt/hgfs/U/RDF2045/model_runs/' + os.path.basename(os.path.normpath(dir_out)))
# shutil.copy(data_out, '/mnt/hgfs/J')
