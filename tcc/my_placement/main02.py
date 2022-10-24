from email.mime import application
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
# from WAPathSelectionNPlacement import WARoutingAndDeploying
# from jsonDynamicPopulation import DynamicPopulation
from placementCloud import JSONPlacementOnlyCloud
# from jsonPopulation import JSONPopulation

"""
Cria aplicações de maneira aleatória.
Aplicações contém Módulos e Mensagens
Módulos: Nome, RAM
Mensagem: Nome, Source, Destiny, IPT, Bytes
"""
def createRandomApplications(fileName):
    applications = {}
    return applications

"""
Carrega uma tolopogia previamente gerada em arquivo JSON.
Topologia contém Nós e Links.
Nós: id, RAM, IPT
Links: id, Source, Destiny, Bandwidth (BW), ... (PR) 
"""
def loadTopolyFromJSON(fileName):
    dataNetwork = {}
    return dataNetwork

def main(simulated_time, path, pathResults, it, idCloud):

    """
    Etapa 1 - Carregar topologia
    """
    fileNameTopology = '.json'
    Nodes = loadTopolyFromJSON(fileNameTopology)

    """
    Etapa 2 - Carregar aplicações.
    """
    fileNameApps = '.json'
    Apps = createRandomApplications(fileNameApps)

    """
    Etapa 3 - Inicialização das Aplicações na "nuvem"
    """
    fileNamePlacement = '.json'
    placement = JSONPlacementOnlyCloud(idcloud=idCloud, json=fileNamePlacement)

    """
    Etapa 4 - Algoritmo de Seletor + Deploy para ser usado na simuação
    """
    selector = MCDARoutingAndDeploying(idcloud=idCloud)

    """
    Etapa 5 - Simualação
    """

    endTime = simulated_time
    s = Sim(Nodes, default_results_path=pathResults)

    """
    Etapa 6 - População
    """
    fileNamePopulation = '.json'

    """
    Etapa 7 - Deploy das Aplicações + Inicio da simulação.
    """
    s.deploy_app(Apps, placement, fileNamePopulation, selector)
    s.run(endTime, test_initial_deploy=False, show_progress_monitor=True)
    s.print_debug_assignaments()


if __name__ == '__main__':

    simulationPeriod = 1000
    idCloud = 100
    main(simulated_time=simulationPeriod, idCloud=100)