"""
    Autor: Matheus Fonseca A. de Oliveira
    Teste 1 - Arquivo base: 01_basicExample
    
    27/08/2022 - Substuição dos arquivos de Topologia, Aplicação, Alocação. - Working
    28/08/2022 - Substuição dos "Users" para Population.

    
"""
import os
import time
import json
import random
import logging.config

import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology
from yafs.population import *

from yafs.placement import *
from yafs.path_routing import DeviceSpeedAwareRouting
from yafs.distribution import deterministic_distribution

pathTopology = "topologies/"
pathApplication = "applications/"
pathAllocation = "allocations/"


def main(stop_time, it,folder_results):

    """
    TOPOLOGY
    """
    t = Topology()

    dataNetwork = json.load(open(pathTopology+'network_15.json'))
    t.load(dataNetwork)
    nx.write_gexf(t.G,"graph_15.gexf") 
    # Abrir arquivo .gexf com Gephi para visualização da topologia.

    print(t.G.nodes())

    """
    APPLICATION or SERVICES
    """
    dataApp = json.load(open(pathApplication+'applications.json'))
    apps = create_applications_from_json(dataApp)

    """
    SERVICE PLACEMENT 
    """
    placementJson = json.load(open(pathAllocation+'allocations.json'))
    placement = JSONPlacement(name="Placement", json=placementJson)

    placement = NoPlacementOfModules('None')

    """
    Defining ROUTING algorithm to define how path messages in the topology among modules
    """
    selectorPath = DeviceSpeedAwareRouting()


    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path=folder_results+"sim_trace_15")

    """
    Deployment of each Application.
    """
    
    for aName in apps.keys():
        s.deploy_app(apps[aName], placement, selectorPath) 

    """
    Deploy users
    """
    userJSON = json.load(open(pathAllocation+'usersDefinition.json'))
    for user in userJSON["sources"]:
        app_name = user["app"]
        app = s.apps[app_name]
        msg = app.get_message(user["message"])
        node = user["id_resource"]
        dist = deterministic_distribution(100, name="Deterministic")
        idDES = s.deploy_source(app_name, id_node=node, msg=msg, distribution=dist)
    """
    Population part 
    1 - Initially copied from old-Tutorial 01.
    """

    # population = Statical("Statical")
    # detDistribution = deterministic_distribution(name="Determenistic",time=100)

    """
    RUNNING - last step
    """
    logging.info(" Performing simulation: %i " % it)
    s.run(stop_time)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()


if __name__ == '__main__':
    LOGGING_CONFIG = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(LOGGING_CONFIG)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"

    nIterations = 1  # iteration for each experiment
    simulationDuration = 20000  

    # Iteration for each experiment changing the seed of randoms
    for iteration in range(nIterations):
        random.seed(iteration)
        logging.info("Running experiment it: - %i" % iteration)

        start_time = time.time()
        main(stop_time=simulationDuration,
             it=iteration,folder_results=folder_results)

        print("\n--- %s seconds ---" % (time.time() - start_time))

    print("Simulation Done!")
  
    # Analysing the results. 
    dfl = pd.read_csv(folder_results+"sim_trace_15"+"_link.csv")
    print("Number of total messages between nodes: %i"%len(dfl))

    df = pd.read_csv(folder_results+"sim_trace_15.csv")
    print("Number of requests handled by deployed services: %i"%len(df))

    dfapp1 = df[df.app == 0].copy() # a new df with the requests handled by app 2
    print(dfapp1.head())
    
    dfapp1.loc[:,"transmission_time"] = dfapp1.time_emit - dfapp1.time_reception # Transmission time
    dfapp1.loc[:,"service_time"] = dfapp1.time_out - dfapp1.time_in

    print("The average service time of app 1 is: %0.3f "%dfapp1["service_time"].mean())

    print("The app 1 is deployed in the folling nodes: %s"%np.unique(dfapp1["TOPO.dst"]))
    print("The number of instances of App 1 deployed is: %s"%np.unique(dfapp1["DES.dst"]))

    # # -- App 2 
    # dfapp2 = df[df.app == 2].copy() # a new df with the requests handled by app 2
    # print(dfapp2.head())
    
    # dfapp2.loc[:,"transmission_time"] = dfapp2.time_emit - dfapp2.time_reception # Transmission time
    # dfapp2.loc[:,"service_time"] = dfapp2.time_out - dfapp2.time_in

    # print("The average service time of app2 is: %0.3f "%dfapp2["service_time"].mean())

    # print("The app2 is deployed in the folling nodes: %s"%np.unique(dfapp2["TOPO.dst"]))
    # print("The number of instances of App2 deployed is: %s"%np.unique(dfapp2["DES.dst"]))
    
    