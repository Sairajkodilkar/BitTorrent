from bittorrent.peers.packetization import *
from bittorrent.piece import *
import errno
import time

MAX_HANDSHAKE_LEN = 304
HANDSHAKE_BUFFER_LEN = 1 << 9  # its greater than the max size to have some buffer
PEER_ID_SIZE = 20


class PeerState:

    def __init__(self, choke=True, interested=False, connected=True):
        self.choke = choke
        self.interested = interested
        self.connected = connected  # specify if peer close the connection


class Peer:

    def __init__(self, socket, pieces):
        self._peer_sock = socket
        try:
            self._peer_address = socket.getpeername()
        except OSError as ose:
            self._peer_address = None
        self._peer_id   = None

        self.peer_state = PeerState()
        self.my_state = PeerState()

        self.start_time = time.time()
        self.keep_alive_timeout = 30
        self.total_data_recvd = 0
        self.total_data_sent = 0

        self.pieces = Pieces(pieces)
        return

    @property
    def peer_sock(self):
        return self._peer_sock

    @property
    def peer_address(self):
        return self._peer_address

    @property
    def peer_id(self):
        return self._peer_id

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
        return self.peer_sock.settimeout(timeout)

    def recv_all(self):
        # recv first 4 bytes to determine the length
        # The user should use try to see if pipe is broken or not
        packet = b''
        while(len(packet) < PacketFormat.INTEGER_SIZE):
            packet += self.peer_sock.recv(
                PacketFormat.INTEGER_SIZE - len(packet))
            self.last_recv_time = time.time()

        if(len(packet) < PacketFormat.INTEGER_SIZE):
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
        if(response[0] == ID.CHOKE):
            self.my_state.choke = True
        elif(response[0] == ID.UNCHOKE):
            self.my_state.choke = False
        elif(response[0] == ID.INTERESTED):
            self.peer_state.interested = True
        elif(response[0] == ID.NOT_INTERESTED):
            self.peer_state.interested = False
        elif(response[0] == ID.HAVE):
            self.pieces.add_piece(response[1])
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
        return

    def send_handshake(
            self, info_hash, peer_id,
            pstr=b"BitTorrent protocol", request=True):

        pkt_content = packetize_handshake(
            len(pstr), pstr, 0, info_hash, peer_id)
        try:
            self.send_packet(pkt_content)
        except ConnectionError:
            self.close()

        handshake_str_len_packet = None
        try:
            handshake_str_len_packet = self.peer_sock.recv(
                PacketFormat.BYTE_SIZE)
        except (ConnectionError, OSError):
            self.close()

        if(not handshake_str_len_packet):
            self.close()  # peer must have closed the tcp connection
            raise ConnectionError

        handshake_str_len = unpacketize_handshake_length(
            handshake_str_len_packet)[0]
        handshake_str_packet = self.peer_sock.recv(handshake_str_len)
        handshake_remaining = self.peer_sock.recv(48)

        handshake_response_packet = (handshake_str_len_packet +
                                     handshake_str_packet + handshake_remaining)

        handshake_response = unpacketize_handshake(handshake_response_packet)
        self.last_recv_time = time.time()
        self.total_data_sent += len(handshake_response_packet)
        self._peer_id = handshake_response[4]

        return handshake_response

    def choke(self, status):
        pkt_content = None
        if(status):
            pkt_content = packetize_choke()
        else:
            pkt_content = packetize_unchoke()
        self.send_packet(pkt_content)
        self.peer_state.choke = status
        return

    def interested(self, status):
        pkt_content = None
        if(status):
            pkt_content = packetize_interested()
        else:
            pkt_content = packetize_notinterested()
        self.send_packet(pkt_content)
        self.my_state.interested = status
        return

    def have(self, piece_index):
        pkt_content = packetize_have(piece_index)
        self.send_packet(pkt_content)
        return

    def send_bitfield(self, bitfield):
        pkt_content = packetize_bitfield(bitfield)
        self.send_packet(pkt_content)
        return

    def request(self, index, begin, length):
        pkt_content = packetize_request(index, begin, length)
        self.send_packet(pkt_content)
        return

    def send_block(self, index, begin, block):
        pkt_content = packetize_piece(index, begin, block)
        self.send_packet(pkt_content)
        return

    def cancel(self, index, begin, length):
        pkt_content = packetize_cancel(index, begin, length)
        self.send_packet(pkt_content)
        return

    def send_port(self, listen_port):
        pkt_content = packetize_port(listen_port)
        self.send_packet(pkt_content)
        return

    def keep_alive(self):
        pkt_content = packetize_keepalive()
        self.send_packet(pkt_content)
        return

    def close(self):
        #print("closing the sock")
        self.peer_sock.close()
        self.my_state.connected = False
        self.peer_state.connected = False
        return

    def get_download_speed(self):
        time_interval = time.time() - self.start_time
        download_speed = self.total_data_recvd / time_interval
        return download_speed

    def get_upload_speed(self):
        time_interval = time.time() - self.start_time
        upload_speed = self.total_data_sent / time_interval
        return upload_speed

    def __repr__(self):
        return str(self.peer_address)
