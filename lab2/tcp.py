import sys
sys.path.append('..')

from src.sim import Sim
from src.connection import Connection
from src.tcppacket import TCPPacket
from src.buffer import SendBuffer,ReceiveBuffer

class TCP(Connection):
    ''' A TCP connection between two hosts.'''
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None,window=1000):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)

        ### Sender functionality

        # send window; represents the total number of bytes that may
        # be outstanding at one time
        self.window = window
        # send buffer
        self.send_buffer = SendBuffer()
        # maximum segment size, in bytes
        self.mss = 1000
        # largest sequence number that has been ACKed so far; represents
        # the next sequence number the client expects to receive
        self.sequence = 0
        # retransmission timer
        self.timer = None
        # timeout duration in seconds
        self.timeout = .2
        self.round_trip_map = {}
        self.rtt_estimates = {}
        #number of total packets
        self.numpackets = 0

        ### Receiver functionality

        # receive buffer
        self.receive_buffer = ReceiveBuffer()
        # ack number to send; represents the largest in-order sequence
        # number not yet received
        self.ack = 0

    def trace(self,message):
        ''' Print debugging messages. '''
        Sim.trace("TCP",message)

    def receive_packet(self,packet):
        ''' Receive a packet from the network layer. '''
        if packet.ack_number > 0:
            # handle ACK
            self.handle_ack(packet)
        if packet.length > 0:
            # handle data
            self.handle_data(packet)

    ''' Sender '''

    def send(self,data):
        ''' Send data on the connection. Called by the application. This
            code currently sends all data immediately. '''
        self.send_buffer.put(data)
        self.send_any_available()
        self.cancel_timer()
        self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    def send_any_available(self):

        while self.send_buffer.available() > 0 and self.send_buffer.outstanding() < self.window:
            #TODO: max, min?
            send_size = min(self.send_buffer.available(), self.mss)
            buffered_data, sequence = self.send_buffer.get(send_size)
            self.send_packet(buffered_data,sequence)



    def send_packet(self,data,sequence):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=data,
                           sequence=sequence,
                           ident=self.numpackets
                        )

        self.numpackets += 1

        # send the packet
        self.trace("%s (%d) sending TCP segment to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)

        self.round_trip_map[packet.ident] = Sim.scheduler.current_time()

        # set a timer
        if not self.timer:
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    def handle_ack(self,packet):
        ''' Handle an incoming ACK. '''
        self.sequence = max(self.sequence, packet.ack_number)
        self.send_buffer.slide(self.sequence)
        self.send_any_available()

        currTime = Sim.scheduler.current_time()
        prevTime = self.round_trip_map[packet.ident]
        self.round_trip_map[packet.ident] =  currTime - prevTime

        if self.send_buffer.outstanding() <= 0:
            self.cancel_timer()

    def retransmit(self,event):
        ''' Retransmit data. '''
        self.trace("%s (%d) retransmission timer fired" % (self.node.hostname,self.source_address))
        self.timer = None

        self.timeout = max(.2, min(2*self.timeout, 60))

        buffered_data, sequence = self.send_buffer.resend(self.mss)
        self.send_packet(buffered_data, sequence)

    def cancel_timer(self):
        ''' Cancel the timer. '''
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None



    ''' Receiver '''

    def handle_data(self,packet):
        ''' Handle incoming data. This code currently gives all data to
            the application, regardless of whether it is in order, and sends
            an ACK.'''
        self.trace("%s (%d) received TCP segment from %d for %d" % (self.node.hostname,packet.destination_address,packet.source_address,packet.sequence))
        self.receive_buffer.put(packet.body, packet.sequence)
        data, sequence = self.receive_buffer.get()
        self.ack = len(data) + sequence
        self.app.receive_data(data)
        self.send_ack(packet.ident)

    def send_ack(self, packetident):
        ''' Send an ack. '''
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           ack_number=self.ack,
                           ident = packetident)
        # send the packet
        self.trace("%s (%d) sending TCP ACK to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)
