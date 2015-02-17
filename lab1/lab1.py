import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

import random

class DelayHandler(object):
    def receive_packet(self,packet):
        print "Current Time",Sim.scheduler.current_time()
        print "Packet ID",packet.ident
        print "Packet Created",packet.created
        print "Current Time - Packet Created Time", Sim.scheduler.current_time() - packet.created
        print "Transmission Delay",packet.transmission_delay
        print "Propagation Delay",packet.propagation_delay
        print "Queuing Delay",packet.queueing_delay
        print "\n"

if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('./two-hops.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')

    n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.get_link('n2'))
    #n2.add_forwarding_entry(address=n2.get_address('n1'),link=n2.get_link('n3'))

    # setup app
    d = DelayHandler()
    #net.nodes['n1'].add_protocol(protocol="delay",handler=d)
    net.nodes['n2'].add_protocol(protocol="delay",handler=d)
    net.nodes['n3'].add_protocol(protocol="delay",handler=d)

    # send one packet
    packets = []
    for i in range(1000):
        newpacket = packet.Packet(destination_address=n1.get_address('n3'),ident=i,protocol='delay',length=1000)
        packets.append(newpacket)

    for p in packets:
        Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)


    # run the simulation
    Sim.scheduler.run()
