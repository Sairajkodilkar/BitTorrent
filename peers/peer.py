'''
Keepalives are generally sent once every two minutes, but note that timeouts can be done much more quickly when data is expected.
Should I include timeout inside or outside
Problems:
    !!!!!The handshake for the peer is sending some reserved byte!!!!!  How to manage all the peers?  there must be one listening thread
        Each peer must have its own thread?
            -But main thread must be able to manage all the thread
            -Main thread should be able to determine download rate and
                determine to choke
            -I might need to make subclass using the threading class and then
                invoke the peer functions on it

        On termination of peer connection the thread must also be closed
        -How to determine if the connections is closed by peer
        -Need to check the socket state every time.

        I should also maintain the states for all the peers:
            Is he chokeing/unchokeing me
            Is he interested/not interested in me
            Am I chokeing/unchokeing him
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

from bittorrent.peers.packetization import *
from bittorrent.piece import *
import errno
import time

MAX_HANDSHAKE_LEN = 304
HANDSHAKE_BUFFER_LEN = 1<<9 #its greater than the max size to have some buffer
PEER_ID_SIZE = 20

class PeerState:

    def __init__(self, choke=True, interested=False, connected=True):
        self.choke      = choke
        self.interested = interested
        self.connected  = connected #specify if peer close the connection


class Peer:

    def __init__(self, socket, pieces):
        self.peer_sock = socket

        self.peer_state = PeerState()
        self.my_state = PeerState()

        self.start_time         = time.time()
        self.keep_alive_timeout = 30
        self.total_data_recvd   = 0
        self.total_data_sent    = 0

        self.pieces = Pieces(pieces)


    @property
    def choked(self):
        return self.peer_state.choke
    
    @property
    def i_am_interested(self):
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
        self.peer_sock.settimeout(timeout)

    def recv_all(self):
        #recv first 4 bytes to determine the length
        #The user should use try to see if pipe is broken or not
        packet = b''
        while(len(packet) < PacketFormat.INTEGER_SIZE):
            packet += self.peer_sock.recv(PacketFormat.INTEGER_SIZE - len(packet))
            self.last_recv_time = time.time()

        if(len(packet) < PacketFormat.INTEGER_SIZE):
            print('return -1', packet)
            return (-1,)

        length = unpacketize_length(packet)[0]
        if(length == 0):
            return (ID.KEEP_ALIVE,)

        data = self.peer_sock.recv(length)
        while(len(data) < length):
            data += self.peer_sock.recv(length - len(data))

        self.last_recv_time = time.time()
        self.total_data_recvd += len(data)

        return self.decode_data(data)

    def decode_data(self, data):
        response = unpacketize_response(data)
        if(response[0] == ID.CHOCK):
            self.my_state.choke = True
        elif(response[0] == ID.UNCHOCK):
            self.my_state.choke = False
        elif(response[0] == ID.INTERESTED):
            self.peer_state.interested = True
        elif(response[0] == ID.NOT_INTERESTED):
            self.peer_state.interested = False
        elif(response[0] == ID.HAVE):
            self.pieces[response[1]].piece_count += 1
        elif(response[0] == ID.BIT_FIELD):
            self.pieces.add_bitfield(response[1])

        return response

    def send_packet(self, pkt_content):
        try:
            self.peer_sock.sendall(pkt_content)
        except OSError:
            self.peer_sock.close()
        self.last_send_time = time.time()
        self.total_data_sent += len(pkt_content)

    def send_handshake(self, info_hash, peer_id, pstr=b"BitTorrent protocol",
                request=True):
        pkt_content = packetize_handshake(len(pstr), pstr, 0, info_hash,
                                        peer_id)
        try:
            self.send_packet(pkt_content)
        except ConnectionError:
            self.close()

        handshake_str_len_packet = None
        try:
            handshake_str_len_packet = self.peer_sock.recv(PacketFormat.BYTE_SIZE)
        except ConnectionError:
            self.close()

        if(not handshake_str_len_packet):
            self.close() #peer must have closed the tcp connection
            raise ConnectionError

        handshake_str_len = unpacketize_handshake_length(handshake_str_len_packet)[0]
        handshake_str_packet = self.peer_sock.recv(handshake_str_len)
        handshake_remaining = self.peer_sock.recv(48)

        handshake_response_packet = (handshake_str_len_packet +
                                    handshake_str_packet + handshake_remaining)

        handshake_response = unpacketize_handshake(handshake_response_packet)
        self.last_recv_time = time.time()
        self.total_data_sent += len(handshake_response_packet)
        return handshake_response

    def choke(self, status):
        pkt_content = None
        if(status):
            pkt_content = packetize_choke()
        else:
            pkt_content = packetize_unchoke()
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

    def keep_alive(self):
        print("sending keep alive")
        pkt_content = packetize_keepalive()
        self.send_packet(pkt_content)

    def close(self):
        self.peer_sock.close()
        self.my_state.connected = False
        self.peer_state.connected = False

    def get_download_speed(self):
        time_interval =  time.time() - self.start_time
        download_speed = self.total_data_recvd / time_interval
        return download_speed

    def get_upload_speed(self):
        time_interval = self.start_time - time.time()
        upload_speed = self.total_data_sent / time_interval
        return upload_speed



