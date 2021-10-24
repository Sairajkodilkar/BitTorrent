'''
Keepalives are generally sent once every two minutes, but note that timeouts can be done much more quickly when data is expected.
Should I include timeout inside or outside
Problems:
    !!!!!The handshake for the peer is sending some reserved byte!!!!!  How to manage all the peers?  there must be one listening thread
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

    def __init__(chock=False, interested=False, connected=True):
        self.chock      = chock
        self.interested = interested
        self.connected  = connected #specify if peer close the connection


class Peer:

    def __init__(self, socket):
        self.peer_sock = socket

        self.peer_state = PeerState()
        self.my_state = PeerState()

        self.timer = time.time()
        self.last_send_time = time.time()
        self.last_recv_time = time.time()
        self.total_data_recvd = 0
        self.total_data_sent = 0

        self.pieces_list = Pieces()

    @property
    def chocked(self):
        return self.peer_state.choke
    
    @property
    def interested(self):
        return self.my_state.interested

    @property
    def choked_me(self):
        return self.my_state.choke

    @property
    def interested_in_me(self):
        return self.peer_state.interested

    @property
    def connected(self):
        return self.peer_state.connected

    def fileno(self):
        return self.peer_sock.fileno()

    def set_timeout(self, timeout):
        self.socket.settimeout(timeout)

    def recv_all(self):
        #recv first 4 bytes to determine the length
        #The user should use try to see if pipe is broken or not
        packet = self.peer_sock.recv(LENGHT_LEN)
        self.last_recv_time = time.time()

        if(not packet):
            return (-1,)

        length_payload = unpacketize_length(packet)
        if(length_payload[0] == 0):
            return 0
        data = length_payload[1]
        while(len(data) < length_payload[0]):
            remaining = length_payload - len(data)
            self.peer_sock.recv(remaining)
            data += length_payload[1]

        self.last_recv_time = time.time()
        self.total_data_recvd += len(data)

        return self.decode_data(data)

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
        elif(response[0] == ID.HAVE):
            self._add_piece(response[1])
        elif(response[0] == ID.BIT_FIELD):
            self.pieces_list.add_bitfield(response[1])

        return response

    def send_packet(self, pkt_content):
        self.peer_sock.sendall(pkt_content)
        self.last_send_time = time.time()
        self.total_data_sent += len(pkt_content)

    def handshake(self, info_hash, peer_id, pstr=b"BitTorrent protocol"):
        pkt_content = packetize_handshake(len(pstr), pstr, 0, info_hash,
                                        peer_id)
        self.send_packet(pkt_content)
        handshake_response_packet = self.peer_sock.recv(HANDSHAKE_BUFFER_LEN)
        handshake_response = unpacketize_handshake(handshake_response_packet)
        self.last_recv_time = time.time()
        self.total_data_sent += len(handshake_response_packet)
        return handshake_response

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

    def send_block(self, index, begin, block):
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
        self.my_state.connected = False
        self.peer_sock.connected = False

    def get_download_speed(self):
        time_interval = self.last_recv_time - time.time()
        download_speed = self.total_data_recvd / time_interval
        return download_speed

    def get_upload_speed(self):
        time_interval = self.last_recv_time - time.time()
        upload_speed = self.total_data_sent / time_interval
        return upload_speed

