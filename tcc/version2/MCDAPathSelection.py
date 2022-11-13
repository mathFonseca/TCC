import networkx as nx
import itertools
import time
import os
import pandas as pd
import operator
from subprocess import Popen, PIPE
from collections import namedtuple
from yafs.selection import Selection
from yafs.topology import *
import operator
import itertools
import numpy as np

NodeDES = namedtuple('NodeDES', ['node', 'des','path'])

class MCDARoutingAndDeploying(Selection):

    def __init__(self, path,pathResults,idcloud,logger=None):
        super(MCDARoutingAndDeploying, self).__init__()
        self.cache = {}
        self.invalid_cache_value = -1
        self.previous_number_of_nodes = -1
        self.idcloud = idcloud

        self.path = path
        pathTMP = "tmp_MCDA"

        self.dname = pathResults + pathTMP
        try:
            os.makedirs(self.dname)
        except OSError:
            None

        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("  MCDA - ELECTRE - Routing, Placement and Selection initialitzed ")

        self.min_path = {}

        self.idEvaluation = 0
        self.controlServices = {}
        # key: a service
        # value : a list of idDevices
        # Note: All services are deployed in the cloud, and they cannot be removed from there.

        self.powermin = []
    """
    It selects all paths
    """


    def get_the_path(self,G,node_src,node_dst):
        self.logger.info(" function: get_the_path activated")
        if (node_src,node_dst) not in self.min_path.keys():
            self.min_path[(node_src, node_dst)]= list(nx.shortest_path(G, source=node_src, target=node_dst))
        return self.min_path[(node_src, node_dst)]

    def compute_NodeDESCandidates(self, node_src, alloc_DES, sim, DES_dst):
        self.logger.info(" function: compute_NodeDESCandidates activated")

        try:
            # print len(DES_dst)
            nodes = []
            for dev in DES_dst:
                # print "DES :",dev
                node_dst = alloc_DES[dev]
                try:
                    nodes.append(self.get_the_path(sim.topology.G, node_src,node_dst))
                    self.logger.info("Appending on node %s" % (node_src))

                except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
                    self.logger.warning("No path between two nodes: %s - %s " % (node_src, node_dst))

            return nodes

        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.logger.warning("No path between from nodes: %s " % (node_src))
            # print "Simulation ends?"
            return []

    def compute_Latency(self,sim,node_src,node_dst):
        self.logger.info(" function: compute_Latency activated")
        try:
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=node_dst))
            totalTimelatency = 0
            for i in range(len(path) - 1):
                link = (path[i], path[i + 1])
                totalTimelatency += sim.topology.G.edges[link][Topology.LINK_PR]
            return totalTimelatency

        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            return 9999999

    def doDeploy(self,sim,app_name,module,id_resource):
        app = sim.apps[app_name]
        services = app.services
        return sim.deploy_module(app_name, module, services[module], [id_resource])


    def print_control_services(self):
        print ("-"*30)
        print (" - Assignaments (node_src,service) -> (PATH, DES) ")
        print ("-" * 30)
        for k in self.controlServices.keys():
            print (k,"->",self.controlServices[k])

        print ("-" * 30)
        return self.controlServices

    """
    This functions is called from the simulator to compute the path between two nodes. Also, it chooses the destination service.

    If the message.src == None, the message is send from a client to a gateway device.
    In this case, we use MCDA process to take an action.
    Actions are:
        - Use the cloud
        - Deploy a new service
        - Move (undeploy and deploy the service)
    """

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        self.logger.info("Function: get_path activated")

        # Entity that sends the message
        node_src = topology_src 

        # Name of the service
        service = message.dst

        # Current ID_processes who run this service: a list
        DES_dst = alloc_module[app_name][message.dst]

        #Node Src: %s, Service: %s"%(node_src,service))
        # print "\t WHERE DEPLOY SERVICE: %s" %message.dst

        # The action depends on the type of service  and the place from it is called.
        if (node_src,service) not in self.controlServices.keys():
            self.logger.info("Take an action on service: %s from node: %i"%(service,node_src))

            mergednodes = sim.topology.G.nodes
            self.logger.info("\t Candidate list: "+str(mergednodes))

            best_node = 150
            
            self.idEvaluation += 1
            des = sim.get_DES_from_Service_In_Node(best_node,app_name,service)
            self.logger.info("RESULTS: bestNODE: %i, DES: %s" % (best_node, des))

            if des == []:
                self.logger.info ("NEW DEPLOYMENT IS REQUIRED in node: %i ",best_node)
                des = self.doDeploy(sim, app_name, service, best_node)

                # sim.print_debug_assignaments()
            else:
                des = [des]
                # print "HERE Node: %i, APP: %s , SERVICE: %s" %(best_node,app_name,service)
                self.logger.info("From node choice: DES: %s " % (des))

            #TODO gestionar best_node action
            path = self.get_the_path(sim.topology.G, node_src, best_node)
            self.controlServices[(node_src,service)] = (path,des)


        path,des = self.controlServices[(node_src,service)]
        self.logger.info("Path %s chose"%path)
        

        return [path],des


