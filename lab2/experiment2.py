import sys
sys.path.append('..')

from src.sim import Sim
from src.node import Node
from src.link import Link
from src.transport import Transport
from tcp import TCP
from plotting import Plotter

from networks.network import Network

import optparse
import os
import subprocess

class AppHandler(object):
    def __init__(self,filename):
        self.filename = filename
        self.directory = 'received'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.filename),'w')
        self.total_bits = 0

    def receive_data(self,data):
        Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
        self.total_bits += len(data)
        self.f.write(data)
        self.f.flush()

class Main(object):
    def __init__(self):
        self.directory = 'received'
        self.parse_options()
        self.run()
        self.diff()

    def parse_options(self):
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--filename",type="str",dest="filename",
                          default='test.txt',
                          help="filename to send")

        parser.add_option("-l","--loss",type="float",dest="loss",
                          default=0.0,
                          help="random loss rate")

        parser.add_option("-w","--window",type="float",dest="window",
                          default=1000,
                          help="random loss rate")

        (options,args) = parser.parse_args()
        self.filename = options.filename
        self.loss = options.loss
        self.window = options.window

    def diff(self):
        args = ['diff','-u',self.filename,self.directory+'/'+self.filename]
        result = subprocess.Popen(args,stdout = subprocess.PIPE).communicate()[0]
        print
        if not result:
            print "File transfer correct!!!"
        else:
            print "File transfer failed. Here is the diff:"
            print
            print result

    def run(self):

        # Run through each window size and simulate transfer
        window_sizes = [1000,2000,5000,10000,15000,20000]
        queueing_times = []

        for size in window_sizes:
            Sim.scheduler.reset()
            Sim.set_debug('AppHandler')
            Sim.set_debug('TCP')

            # setup network
            net = Network('../networks/lab2-test1.txt')
            net.loss(self.loss)

            # setup routes
            n1 = net.get_node('n1')
            n2 = net.get_node('n2')
            n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
            n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

            # setup transport
            t1 = Transport(n1)
            t2 = Transport(n2)

            # setup application
            a = AppHandler(self.filename)

            # setup connection
            c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a,window=size)
            c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a,window=size)

            # send a file
            with open(self.filename,'r') as f:
                while True:
                    data = f.read(1000)
                    if not data:
                        break
                    Sim.scheduler.add(delay=0, event=data, handler=c1.send)

            # run the simulation
            Sim.scheduler.run()
            queueing_times.append(c2.total_queue_time/c2.numpackets)

        print queueing_times
        # Graphing
        p = Plotter()
        p.linePlotData(window_sizes,queueing_times,'Window Size','Throughput',"queuetimes")

if __name__ == '__main__':
    m = Main()
