'''
Keepalives are generally sent once every two minutes, but note that timeouts can be done much more quickly when data is expected.
Should I include timeout inside or outside
Problems:
    !!!!!The handshake for the peer is sending some reserved byte!!!!!
    How to manage all the peers?
        there must be one listening thread
        Each peer must have its own thread?
            -But main thread must be able to manage all the thread
            -Main thread should be able to determine download rate and
                determine to chock
            -I might need to make subclass using the threading class and then
                invoke the peer functions on it

        On termination of peer connection the thread must also be closed
        -How to determine if the connections is closed by peer
        -Need to check the socket state every time.

        I should also maintain the states for all the peers:
            Is he chocking/unchocking me
            Is he interested/not interested in me
            Am I chocking/unchocking him
            Am I interested/not interested in him

    What exactly is the max block size?
        There is conflict on this topic

    How to manange all the pieces since they will come in block of small size?
        There must be lock on the piece
        If two client send same block then we must select which block write.
        There must be global piece state

    How to request blocks?
        Should I request all of them to all the peers or should I request
        different blocks to differnet peers

    Thoughts on pipeline:
        All the sending function will put the packets on the common queue and
        queue will be emptied by a different thread

'''

from packetization import *
import time

MAX_HANDSHAKE_LEN = 304
HANDSHAKE_BUFFER_LEN = 1<<9 #its greater than the max size to have some buffer

class PeerState:

    def __init__(chock=False, interested=False, close=False):
        self.chock      = chock
        self.interested = interested
        self.close      = close         #specify if peer close the connection


def get_speed(data_size, time_interval_ns):

    return data_size / (time_interval_ns * 1e-9)


class Peer:

    def __init__(self, socket):
        self.peer_sock = socket

        self.peer_state = PeerState()
        self.my_state = PeerState()

        self._download_speed = 0
        self._upload_speed = 0

        self.timer = time.time()
        self.last_send_time = time.time()
        self.last_recv_time = time.time()

    def fileno(self):
        return self.peer_sock.fileno()

    @property
    def download_speed(self):
        return self._download_speed

    @property
    def upload_speed(self):
        return self._upload_speed

    def set_timeout(self, timeout):
        self.socket.settimeout(timeout)

    def recv_all(self, bufsize):
        #recv first 4 bytes to determine the length
        start = time.time_ns()
        packet = self.peer_sock.recv(LENGHT_LEN)

        self.last_recv_time = time.time()

        if(not packet):
            end = time.time_ns()
            #download speed is the average of the previous speed and the
            #current speed
            self._download_speed = ((get_speed(len(ppacket), end - start)
                                    + self._download_speed) / 2)
            return (-1,)

        length_payload = unpacketize_length(packet)

        if(length_payload[0] == 0):
            return 0

        data = length_payload[1]
        while(len(data) < length_payload[0]):
            remaining = length_payload - len(data)
            self.peer_sock.recv(remaining)
            data += length_payload[1]

        end = time.time_ns()
        self._download_speed = ((get_speed(len(packet), end - start)
                                + self._download_speed) / 2)

        return data 

    def decode_data(self, data):
        response = unpacketize_response(data)
        if(response[0] == ID.CHOCK):
            self.my_state.chock = True
        elif(response[0] == ID.UNCHOCK):
            self.my_state.chock = False
        elif(response[0] == ID.INTERESTED):
            self.peer_state.interested = True
        elif(response[0] == ID.NOT_INTERESTED):
            self.peer_state.interested = False

        return data

    def send_packet(pkt_content):

        start = time.time()
        self.peer_sock.sendall(pkt_content)
        self.last_send_time = end = time.time()

        self._upload_speed = ((get_speed(len(pkt_content), end - start)
                            + self._upload_speed) / 2)
        

    def handshake(self, info_hash, peer_id, pstr=b"BitTorrent protocol"):
        pkt_content = packetize_handshake(len(pstr), pstr, 0, info_hash,
                                        peer_id)
        self.send_packet(pkt_content)
        handshake_response = unpacketize_handshake(self.peer_sock.recv(HANDSHAKE_BUFFER_LEN))
        self.last_recv_time = time.time()

    def chock(self, status):
        pkt_content = None
        if(status):
            pkt_content = packetize_chock()
        else:
            pkt_content = packetize_unchock()
        self.send_packet(pkt_content)
        self.peer_state.choke = status

    def interested(self, status):
        pkt_content = None
        if(status):
            pkt_content = packetize_interested()
        else:
            pkt_content = packetize_notinterested()
        self.send_packet(pkt_content)
        self.my_state.interested = status

    def have(self, piece_index):
        pkt_content = packetize_have(piece_index)
        self.send_packet(pkt_content)

    def send_bitfield(self, bitfield):
        pkt_content = packetize_bitfield(bitfield)
        self.send_packet(pkt_content)

    def request(self, index, begin, length):
        pkt_content = packetize_request(index, begin, length)
        self.send_packet(pkt_content)

    def send_piece(self, index, begin, block):
        pkt_content = packetize_piece(index, begin, block)
        self.send_packet(pkt_content)

    def cancel(self, index, begin, length):
        pkt_content = packetize_cancel(index, begin, length)
        self.send_packet(pkt_content)

    def send_port(self, listen_port):
        pkt_content = packetize_port(listen_port)
        self.send_packet(pkt_content)

    def close(self):
        self.peer_sock.close()
        self.my_state.close = True
        
