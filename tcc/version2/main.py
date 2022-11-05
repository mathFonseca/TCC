
import os
import time
import json
import networkx as nx
import logging.config
import collections
import pickle
import random
import numpy as np

from yafs.core import Sim
from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.distribution import *

from yafs.placement import JSONPlacement
from MCDAPathSelection import MCDARoutingAndDeploying
from jsonDynamicPopulation import DynamicPopulation
from placementCloud import JSONPlacementOnlyCloud
# from jsonPopulation import JSONPopulation

def createApplicationFromJson(data):
    applications = {}

    # Aplicações
    for app in data:
        a =  Application(name = app["name"])

        # Source não tem nome aparentemente 
        modules = [{"None": {"Type": Application.TYPE_SOURCE}}]

        # Para cada modulo, dá um append na lista acima.
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        
        # Configura todos os módulos da Aplicação.
        a.set_modules(modules)

        # Mensagens dessa aplicação
        messages = {}
        for message in app["message"]:
            logging.info("Criando mensagem: %s" %message["name"])
            messages[message["name"]] = Message(message["name"], message["s"], message["d"], instructions=message["instructions"], bytes=message["bytes"])

            # Mensagens que surgem da source (sem nó em específico)
            if message["s"] == "None":
                a.add_source_messages(messages[message["name"]])

        # Usar .keys() retorna número de itens de um... container
        logging.info("Total de mensagens criadas: %i" %len(messages.keys()))

        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"], messages[message["message_in"]], messages[message["message_out"]], uniformDistribution, threshold=1.0)

            else:
                a.add_service_module(message["module"], messages[message["message_in"]])
        
        applications[app["name"]] = a
    return applications

def main(simulated_time, case, idCloud):


    pathResults = 'results/'

    t = Topology()
    dataNetwork = json.load(open('topologies/networkDefinition.json'))
    t.load(dataNetwork)
    # t.write('topologies/network_teste.gexf')


    dataApps = json.load(open('applications/appDefinition.json'))
    apps = createApplicationFromJson(dataApps)
    
    for app in apps:
        print(apps[app])

    placementJson = json.load(open('allocations/allocDefinition.json'))
    placement = JSONPlacementOnlyCloud(name="Cloud Alloc",idcloud=idCloud, json=placementJson)
    print("Placement... completed.")
    
    # TODO: Simulator function here

    selectorPath = MCDARoutingAndDeploying(path="",pathResults=pathResults,idcloud=idCloud)

    stop_time = simulated_time
    s = Sim(t, default_results_path=pathResults + "Results_%s_%i" % (case, stop_time))

    # TODO: Population

    dataPopulation = json.load(open('allocations/usersDefinition.json'))

    # Each application has an unique population politic
    # For the original json, we filter and create a sub-list for each app politic
    for aName in apps.keys():
        data = []
        for element in dataPopulation["sources"]:
            if element['app'] == aName:
                data.append(element)

        distribution = exponentialDistribution(name="Exp", lambd=random.randint(100,1000), seed= int(aName)*100)
        pop_app = DynamicPopulation(name="Dynamic_%s" % aName, data=data, activation_dist=distribution)
        # s.deploy_app(apps[aName], placement, pop_app, selectorPath)
        s.deploy_app2(apps[aName], placement, pop_app, selectorPath)
        #s.deploy_app2()
        logging.info("Deploying app: %i" %int(aName))

    logging.info(" Performing simulation: %s "%(case))
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False)  # TEST to TRUE
    logging.info(" End of Simulation")



logging.config.fileConfig(os.getcwd() + '/logging.ini')
if __name__ == '__main__':

    simulationPeriod = 1000000
    datestamp = time.strftime('%Y%m%d')
    idCloud = 3


    start_time = time.time()
    main(simulated_time=simulationPeriod, case='01', idCloud=3)
    print("\n--- %s seconds ---" % (time.time() - start_time))

