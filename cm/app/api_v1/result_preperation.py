import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import shutil
import configparser

#path = os.path.dirname(os.path.abspath(__file__))
SD = "my_calculation_module_directory"
path = os.path.dirname(os.path.abspath(__file__)).split(SD)[0] + "/%s" % SD

if path not in sys.path:
    sys.path.append(path)
from CM.helper_functions.readCsvData import READ_CSV_DATA

def linear_interpol(y0,x0, y1,x1, x):
    return (y0*(x1-x) + y1*(x-x0))/(x1-x0)

def dfToCSV(results, output_dir, scen, filename):
    output_dir = os.path.join(output_dir,scen + '_final')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)
    else:
        os.mkdir(output_dir)
    output_file = os.path.join(output_dir,filename)
    results.transpose().to_csv(output_file)
    return output_dir

def printPlots(results, output_directory):
    """
    Estimated heated area total: gfa_fut
    Estimated heated area per construction period: gfa_xx_fut
    Estimated heated area per capita: gfa_per_cap_fut

    Energy Consumption total: ene_fut
    Energy Consumption per construction period: ene_xx_fut

    Estimated specific Energy Consumption: spec_ene_fut
    Estimated specific Energy Consumption per construction period: spec_ene_xx_fut

    Estimated population grow: pop_fut
    """

    ##########
    # Heated area plot
    ##########
    matplotlib.rcParams['interactive'] == False
    results = results.transpose()
    year = list(results.index)

    fig = plt.figure(figsize = (10,5))
    ax1 = plt.subplot(1,2,1)
    ax1.plot(year, results['gfa_fut'] / 10 ** 6, label='total', color='blue')
    ax1.set(xlabel='year', ylabel='total estimated heated area [Mio m2]')
    ax1.grid()

    ax2 = plt.subplot(1, 2, 2)
    ax2.plot(year, results['gfa_75_fut']/10**6, label='75', color = 'red')
    ax2.plot(year, results['gfa_80_fut']/10**6, label='80', color =  'orange')
    ax2.plot(year, results['gfa_00_fut']/10**6, label='00', color =  'green')
    ax2.plot(year, results['gfa_new_fut']/10**6, label='new_buildings', color =  'purple')
    ax2.legend()
    ax2.set(xlabel='year', ylabel='Estimated heated area per construction period [Mio m2]')
    ax2.grid()
    plt.tight_layout()
    fig.savefig(os.path.join(output_directory,"Estimated_heated_area.png"))
    plt.close()
    #plt.show()

    ##########
    # Heated are per capita plot
    ##########
    fig, ax = plt.subplots()
    ax.plot(year, results['gfa_per_cap_fut'], label='gfa_per_cap')
    ax.set(xlabel='year', ylabel='Estimated heated area per capita [m2/capita]')
    ax.grid()
    fig.savefig(os.path.join(output_directory, "Estimated_specific_energy_consumption.png"))
    plt.close()
    #plt.show()

    ##########
    # Energy consumption plot
    ##########
    fig = plt.figure(figsize = (10,5))
    ax1 = plt.subplot(1,2,1)
    ax1.plot(year, results['ene_fut'] / 10 ** 3, label='total')
    ax1.set(xlabel='year', ylabel='Total estimated Energy Consumption [GWh]')
    ax1.grid()

    ax2 = plt.subplot(1, 2, 2)
    ax2.plot(year, results['ene_75_fut'] / 10 ** 3, label='75')
    ax2.plot(year, results['ene_80_fut'] / 10 ** 3, label='80')
    ax2.plot(year, results['ene_00_fut'] / 10 ** 3, label='00')
    ax2.plot(year, results['ene_new_fut'] / 10 ** 3, label='new_buildings')
    ax2.set(xlabel='year', ylabel='Estimated Energy Consumption per construction period [GWh]')
    ax2.grid()
    ax2.legend()
    fig.savefig(os.path.join(output_directory, "Estimated_energy_consumption.png"))
    plt.close()
    #plt.show()

    ##########
    # Specific Energy consumption plot
    ##########

    fig, ax = plt.subplots()
    ax.plot(year, results['spe_ene_fut'], label='total')
    ax.plot(year, results['spec_ene_75_fut'], label='75')
    ax.plot(year, results['spec_ene_80_fut'], label='80')
    ax.plot(year, results['spec_ene_00_fut'], label='00')
    ax.plot(year, results['spec_ene_new_fut'], label='new')
    ax.set(xlabel='year', ylabel='Specific Energy Consumption [kWh/m2]')
    ax.grid()
    plt.legend()
    fig.savefig(os.path.join(output_directory, "Estimated_specific_energy_consumption.png"))
    plt.close()
    #plt.show()

    ##########
    # Human population grow plot
    ##########

    fig, ax = plt.subplots()
    ax.plot(year, results['pop_fut'], label='population')
    ax.set(xlabel='year', ylabel='Estimated population grow [tsd. people]')
    ax.grid()
    fig.savefig(os.path.join(output_directory, "Estimated_population_grow.png"))
    plt.close()
    #plt.show()
    print("Exported plots to '%s'" % output_directory)

    
def main(input_directory, output_dir, interpol):
    dir_list = os.listdir(input_directory)
    scen_list = {}
    year_list = []
    for item in dir_list:
        if '.' in item: continue
        if item[:-5] not in scen_list.keys():
            scen_list[item[:-5]] = []
        if item[-4:] not in scen_list[item[:-5]]:
            scen_list[item[:-5]].append(item[-4:])
    for scen in scen_list.keys():
        scen_list[scen].sort()
        if len(scen_list[scen]) != 2: continue
        input_scenario_path_1 = os.path.join(input_directory, scen +'_'+ scen_list[scen][0],'indicators_exact.csv')
        input_scenario_path_2 = os.path.join(input_directory, scen + '_' + scen_list[scen][1], 'indicators_exact.csv')
        results_baseyear = pd.read_csv(input_scenario_path_1,index_col = 0, header = 0, skiprows = [1]) # import here with pandas
        results_futureyear = pd.read_csv(input_scenario_path_2,index_col = 0, header = 0, skiprows = [1])
        baseyear = int(results_baseyear.loc['target_year'][0])
        futureyear = int(results_futureyear.loc['target_year'][0])
        results_baseyear.rename(columns={results_baseyear.columns[0]:baseyear},
                                inplace = True)
        results_futureyear.rename(columns={results_futureyear.columns[0]:futureyear},
                                  inplace = True)
        results = results_baseyear.copy()
        results = results.join(results_futureyear)
        if interpol == 'linear':
            for year in range(2020, 2050,5):
                results[year] = linear_interpol(results_baseyear[baseyear],baseyear,
                                                results[futureyear],futureyear,
                                                year)
        else:
            print(interpol + " is not implemented. Use 'linear' instead")
        out_path_final = dfToCSV(results, output_dir,scen, 'results.csv')
        printPlots(results,out_path_final)

if __name__ == '__main__':
    configfile_location = 'result_preperation_conf.ini'
    config = configparser.ConfigParser()
    if not config.read(configfile_location):
        raise AttributeError("Couldn't load configuration file ",
                             configfile_location)
    if config['machine']['machine'] == 'server':
        input_paths_label = 'proj_path_' + 'server'
        proj_path = modProjectPath(config[input_paths_label]['proj_path'])
    elif config['machine']['machine'] == 'local':
        input_paths_label = 'proj_path_' + 'local'
        proj_path = str(config[input_paths_label]['proj_path'])
    else:
        raise AttributeError("No selected machine in configuration file")

    data_warehouse = os.path.join(proj_path, config['input_paths']['data_warehouse'])
    output_dir = os.path.join(proj_path, config['input_paths']['output_dir'])
    if not os.path.exists(data_warehouse):
        raise FileNotFoundError(data_warehouse)
    for region in os.listdir(data_warehouse):
        directory = os.path.join(data_warehouse, region)
        #input_dir_ = "E:/projects2/bmayr_workspace/projects_bernhard/outputs/res_h_regions_test/FR - CCSB"
        output_dir_ = os.path.join(output_dir,region)
        if os.path.exists(output_dir_):
            shutil.rmtree(output_dir_)
            os.mkdir(output_dir_)
        else:
            try:
                os.mkdir(output_dir_)
            except FileNotFoundError:
                os.makedirs(output_dir_)
        interpol_ = 'linear'
        main(directory, output_dir_, interpol_)
    print("DONE")
    print("#"*10)