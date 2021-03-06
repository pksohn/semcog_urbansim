import pandas as pd
import os
import orca
import time
from collections import defaultdict


def orca_year_dataset(hdf, year):
    if str(year) == '2015':
        year = 'base'
    orca.add_injectable("jobs_large_area_lookup", [])
    orca.add_injectable("households_large_area_lookup", [])
    orca.add_injectable("year", int(year if str(year) != 'base' else 2015))
    for tbl in ['households', 'persons', 'jobs', 'buildings', 'parcels', 'dropped_buildings']:
        name = str(year) + '/' + tbl
        if name in hdf:
            df = hdf[name]
        else:
            stub_name = str(2016) + '/' + tbl
            print "No table named " + name + ". Using the structuer from " + stub_name + "."
            df = hdf[stub_name].iloc[0:0]
        orca.add_table(tbl, df)
        orca.clear_cache()


@orca.column('households', cache=True, cache_scope='iteration')
def seniors(persons):
    persons = persons.to_frame(['household_id', 'age'])
    return persons[persons.age >= 65].groupby('household_id').size()


def make_indicators(tab, geo_id):
    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh(households):
        households = households.to_frame([geo_id])
        return households.groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop(households):
        households = households.to_frame([geo_id, 'persons'])
        return households.groupby(geo_id).persons.sum()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def housing_units(buildings):
        buildings = buildings.to_frame([geo_id, 'residential_units'])
        return buildings.groupby(geo_id).residential_units.sum()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def buildings(buildings):
        buildings = buildings.to_frame([geo_id])
        return buildings.groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def household_size():
        df = orca.get_table(tab)
        df = df.to_frame(['hh', 'hh_pop'])
        return df.hh_pop / df.hh

    @orca.column(tab, cache=True, cache_scope='iteration')
    def vacant_units():
        df = orca.get_table(tab)
        df = df.to_frame(['hh', 'housing_units'])
        return df.housing_units - df.hh

    @orca.column(tab, cache=True, cache_scope='iteration')
    def vacancy_rate():
        df = orca.get_table(tab)
        df = df.to_frame(['vacant_units', 'housing_units'])
        return df.vacant_units / df.housing_units

    @orca.column(tab, cache=True, cache_scope='iteration')
    def incomes_1(households):
        households = households.to_frame([geo_id, 'income_quartile'])
        return households[households.income_quartile == 1].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def incomes_2(households):
        households = households.to_frame([geo_id, 'income_quartile'])
        return households[households.income_quartile == 2].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def incomes_3(households):
        households = households.to_frame([geo_id, 'income_quartile'])
        return households[households.income_quartile == 3].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def incomes_4(households):
        households = households.to_frame([geo_id, 'income_quartile'])
        return households[households.income_quartile == 4].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def with_children(households):
        households = households.to_frame([geo_id, 'children'])
        return households[households.children > 0].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def without_children(households):
        households = households.to_frame([geo_id, 'children'])
        return households[households.children.fillna(0) == 0].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def with_seniors(households):
        households = households.to_frame([geo_id, 'seniors'])
        return households[households.seniors > 0].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def without_seniors(households):
        households = households.to_frame([geo_id, 'seniors'])
        return households[households.seniors.fillna(0) == 0].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_size_1(households):
        households = households.to_frame([geo_id, 'persons'])
        return households[households.persons == 1].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_size_2(households):
        households = households.to_frame([geo_id, 'persons'])
        return households[households.persons == 2].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_size_3p(households):
        households = households.to_frame([geo_id, 'persons'])
        return households[households.persons >= 3].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_race_1(persons):
        persons = persons.to_frame([geo_id, 'race_id'])
        return persons[persons.race_id == 1].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_race_2(persons):
        persons = persons.to_frame([geo_id, 'race_id'])
        return persons[persons.race_id == 2].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_race_3(persons):
        persons = persons.to_frame([geo_id, 'race_id'])
        return persons[persons.race_id == 3].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_race_4(persons):
        persons = persons.to_frame([geo_id, 'race_id'])
        return persons[persons.race_id == 4].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_00_04(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[(persons.age <= 4)].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_05_17(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[(persons.age >= 5) & (persons.age <= 17)].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_18_24(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[(persons.age >= 18) & (persons.age <= 24)].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_25_34(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[(persons.age >= 25) & (persons.age <= 34)].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_35_64(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[(persons.age >= 35) & (persons.age <= 64)].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def hh_pop_age_65_inf(persons):
        persons = persons.to_frame([geo_id, 'age'])
        return persons[persons.age >= 65].groupby(geo_id).size()

    @orca.column(tab, cache=True, cache_scope='iteration')
    def jobs_total(jobs):
        jobs = jobs.to_frame([geo_id])
        return jobs.groupby(geo_id).size()

    def make_job_sector_ind(i):
        @orca.column(tab, 'jobs_sec_' + str(i).zfill(2), cache=True, cache_scope='iteration')
        def jobs_sec_id(jobs):
            jobs = jobs.to_frame([geo_id, 'sector_id'])
            return jobs[jobs.sector_id == i].groupby(geo_id).size()

    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
        make_job_sector_ind(i)


def main(run_name):
    outdir = run_name.replace('.h5', '')
    if not (os.path.exists(outdir)):
        os.makedirs(outdir)
    out_annual = os.path.join(outdir, 'annual')
    if not (os.path.exists(out_annual)):
        os.makedirs(out_annual)

    with open(os.path.join(outdir, "runnum.txt"), "w") as runnum:
        runnum.write(os.path.basename(os.path.normpath(outdir)))

    store_la = pd.HDFStore(run_name, mode='r')

    for tbl in ['semmcds', 'zones', 'large_areas']:
        orca.add_table(tbl, store_la['base/' + tbl])

    @orca.column('semmcds', cache=True, cache_scope='iteration')
    def large_area_id(parcels):
        parcels = parcels.to_frame(['semmcd', 'large_area_id'])
        return parcels.drop_duplicates('semmcd').set_index('semmcd').large_area_id

    p = orca.get_table('parcels')
    p = p.to_frame(['city_id', 'large_area_id'])
    cities = p.drop_duplicates('city_id').set_index('city_id')

    orca.add_table('cities', cities)

    for tab, geo_id in [('cities', 'city_id'),
                        ('semmcds', 'semmcd'),
                        ('zones', 'zone_id'),
                        ('large_areas', 'large_area_id')]:
        make_indicators(tab, geo_id)


        # add more indicator
        # geo level: school district

        # 4) pro forma changes by counts, and building types; trace relocating HHs

    years = range(2015, 2045 + 1)
    year_names = ["yr" + str(i) for i in years]
    indicators = ['hh', 'hh_pop', 'housing_units', 'buildings', 'household_size', 'vacant_units', 'vacancy_rate',
                  'incomes_1', 'incomes_2', 'incomes_3', 'incomes_4',
                  'with_children', 'without_children',
                  'with_seniors', 'without_seniors',
                  'hh_size_1', 'hh_size_2', 'hh_size_3p',
                  'hh_pop_race_1', 'hh_pop_race_2', 'hh_pop_race_3', 'hh_pop_race_4',
                  'hh_pop_age_00_04', 'hh_pop_age_05_17', 'hh_pop_age_18_24', 'hh_pop_age_25_34',
                  'hh_pop_age_35_64', 'hh_pop_age_65_inf',
                  'jobs_total', 'jobs_sec_01', 'jobs_sec_02', 'jobs_sec_03',
                  'jobs_sec_04', 'jobs_sec_05', 'jobs_sec_06', 'jobs_sec_07',
                  'jobs_sec_08', 'jobs_sec_09', 'jobs_sec_10', 'jobs_sec_11',
                  'jobs_sec_12', 'jobs_sec_13', 'jobs_sec_14', 'jobs_sec_15',
                  'jobs_sec_16', 'jobs_sec_17', 'jobs_sec_18',
                  ]

    geom = ['cities', 'large_areas', 'semmcds', 'zones']

    start = time.clock()
    dict_ind = defaultdict(list)
    for year in years:
        print 'processing ', year
        orca_year_dataset(store_la, year)
        for tab in geom:
            dict_ind[tab].append(orca.get_table(tab).to_frame(indicators))
    end = time.clock()
    print "runtime:", end - start

    # region should have same value no matter how you slice it.
    df = pd.DataFrame()
    for tab in list(dict_ind):
        for year, year_data in zip(year_names, dict_ind[tab]):
            df[(year, tab)] = year_data.sum()
    df = df.T
    df.index = pd.MultiIndex.from_tuples(df.index)
    df = df.sort_index().sort_index(1)
    del df['vacancy_rate']
    del df['household_size']
    sumstd = df.groupby(level=0).std().sum().sort_values()
    print sumstd[sumstd > 0]

    print df[sumstd[sumstd > 0].index]

    # Todo: add part of fenton to semmcd table
    print set(orca.get_table('semmcds').to_frame(indicators).hh_pop.index) ^ set(orca.get_table('semmcds').hh_pop.index)

    start = time.clock()
    for tab in geom:
        print tab
        writer = pd.ExcelWriter(os.path.join(outdir, tab + "_by_indicator_for_year.xlsx"))
        for i, y in list(enumerate(year_names))[::5]:
            df = dict_ind[tab][i]
            df = df.fillna(0)
            df = df.sort_index().sort_index(1)
            df.to_excel(writer, y)
        writer.save()

        writer = pd.ExcelWriter(os.path.join(out_annual, tab + "_by_indicator_for_year.xlsx"))
        for i, y in enumerate(year_names):
            df = dict_ind[tab][i]
            df = df.fillna(0)
            df = df.sort_index().sort_index(1)
            df.to_excel(writer, y)
        writer.save()

        writer = pd.ExcelWriter(os.path.join(outdir, tab + "_by_year_for_indicator.xlsx"))
        if tab == 'cities':
            la_id = orca.get_table(tab).large_area_id
        if tab == 'semmcds':
            la_id = orca.get_table(tab).large_area_id
            # name = orca.get_table(tab).city_name
        if tab == 'large_areas':
            name = orca.get_table(tab).large_area_name
        for ind in indicators:
            df = pd.concat([df[ind] for df in dict_ind[tab][::5]], axis=1)
            df.columns = year_names[::5]
            if tab == 'cities':
                df["large_area_id"] = la_id
                df.set_index("large_area_id", drop=True, append=True, inplace=True)
            if tab == 'semmcds':
                df["large_area_id"] = la_id
                df.set_index("large_area_id", drop=True, append=True, inplace=True)
            if tab == 'large_areas':
                df["large_area_name"] = name
                df.set_index("large_area_name", drop=True, append=True, inplace=True)
            if len(df.columns) > 0:
                print "saving:", ind
                df = df.fillna(0)
                df = df.sort_index().sort_index(1)
                df.to_excel(writer, ind)
            else:
                print "somtning is wrong with:", ind
        writer.save()

        writer = pd.ExcelWriter(os.path.join(out_annual, tab + "_by_year_for_indicator.xlsx"))
        if tab == 'cities':
            la_id = orca.get_table(tab).large_area_id
        if tab == 'semmcds':
            la_id = orca.get_table(tab).large_area_id
            # name = orca.get_table(tab).city_name
        if tab == 'large_areas':
            name = orca.get_table(tab).large_area_name
        for ind in indicators:
            df = pd.concat([df[ind] for df in dict_ind[tab]], axis=1)
            df.columns = year_names
            if tab == 'cities':
                df["large_area_id"] = la_id
                df.set_index("large_area_id", drop=True, append=True, inplace=True)
            if tab == 'semmcds':
                df["large_area_id"] = la_id
                df.set_index("large_area_id", drop=True, append=True, inplace=True)
            if tab == 'large_areas':
                df["large_area_name"] = name
                df.set_index("large_area_name", drop=True, append=True, inplace=True)
            if len(df.columns) > 0:
                print "saving:", ind
                df = df.fillna(0)
                df = df.sort_index().sort_index(1)
                df.to_excel(writer, ind)
            else:
                print "somtning is wrong with:", ind
        writer.save()
    end = time.clock()
    print "runtime:", end - start

    start = time.clock()
    for year in [2015, 2030, 2045]:
        print "buildings for", year
        orca_year_dataset(store_la, year)
        buildings = orca.get_table('buildings')
        df = buildings.to_frame(buildings.local_columns + ['city_id', 'large_area_id', 'x', 'y'])
        df = df[df.building_type_id != 99]
        df = df.fillna(0)
        df = df.sort_index().sort_index(1)
        df.to_csv(os.path.join(outdir, "buildings_yr" + str(year) + ".csv"))

        persons = orca.get_table('persons')
        df = persons.to_frame(persons.local_columns + ['city_id', 'large_area_id'])
        df = df.fillna(0)
        df = df.sort_index().sort_index(1)
        df.to_csv(os.path.join(outdir, "hh_persons_yr" + str(year) + ".csv"))

        households = orca.get_table('households')
        df = households.to_frame(households.local_columns + ['city_id', 'large_area_id'])
        df = df.fillna(0)
        df = df.sort_index().sort_index(1)
        df.to_csv(os.path.join(outdir, "households_yr" + str(year) + ".csv"))
    end = time.clock()
    print "runtime:", end - start

    start = time.clock()
    years = range(2016, 2045 + 1)
    year_names = ["yr" + str(i) for i in years]
    writer = pd.ExcelWriter(os.path.join(outdir, "buildings_dif_by_year.xlsx"))
    for year, year_name in zip(years, year_names):
        print "buildings for", year
        orca_year_dataset(store_la, year)
        buildings = orca.get_table('buildings')
        df = buildings.to_frame(buildings.local_columns + ['city_id', 'large_area_id'])
        df = df[df.year_built == year]
        df = df.fillna(0)
        df = df.sort_index().sort_index(1)
        df.to_excel(writer, "const_" + year_name)

        demos = orca.get_table('dropped_buildings')
        df = demos.to_frame(demos.local_columns + ['city_id', 'large_area_id'])
        df = df[df.year_demo == year]
        df = df.fillna(0)
        df = df.sort_index().sort_index(1)
        df.to_excel(writer, "demo_" + year_name)

    writer.save()
    end = time.clock()
    print "runtime:", end - start

    store_la.close()
