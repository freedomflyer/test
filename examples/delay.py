import sys
import matplotlib
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet


from networks.network import Network

import random

class Generator(object):
    def __init__(self,node,destination,load,duration):
        self.node = node
        self.load = load
        self.duration = duration
        self.start = 0
        self.ident = 1
        self.destination = destination

    def handle(self,event):
        # quit if done
        now = Sim.scheduler.current_time()
        if (now - self.start) > self.duration:
            return

        # generate a packet
        self.ident += 1
        p = packet.Packet(destination_address=self.destination,ident=self.ident,protocol='delay',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)
        # schedule the next time we should generate a packet
        Sim.scheduler.add(delay=random.expovariate(self.load), event='generate', handler=self.handle)

class DelayHandler(object):
    def __init__(self):
        self.iteration = 0
        print "It\tCurrent Time\tPacket Ident\tCreated At\tElapsed Time\tTransm Delay\tProp Delay\tQueue Delay"

    def receive_packet(self, packet):
        self.iteration += 1
        print "%d\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % \
              (self.iteration, Sim.scheduler.current_time(), packet.ident, packet.created, \
              (Sim.scheduler.current_time() - packet.created), packet.transmission_delay, \
              packet.propagation_delay, packet.queueing_delay)

if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/one-hop.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay",handler=d)

    # setup packet generator
    destination = n2.get_address('n1')
    max_rate = 1000000/(1000*8)
    load = .8  *max_rate
    g = Generator(node=n1,destination=destination,load=load,duration=10)
    Sim.scheduler.add(delay=0, event='generate', handler=g.handle)
    
    # run the simulation
    Sim.scheduler.run()

#141	9.989235	142.000000	9.980235	0.009000	0.008000	0.001000	0.000000
#962	10.009724	963.000000	9.995443	0.014281	0.008000	0.001000	0.005281