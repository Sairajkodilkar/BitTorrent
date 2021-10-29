from bittorrent.bdencoder.bdencoder import Bdecoder, Bencoder
from bittorrent.peers.peer import Peer, PEER_ID_SIZE
from bittorrent.torrent import Torrent, TorrentStatus
from bittorrent.request import httprequest, udprequest
from bittorrent.fileio import FileArray
from bittorrent.swarm import handle_peer
from bittorrent.parse import parse_compact_peers, parse_scrape_res
from bittorrent.piece import Piece, Pieces
from urllib.parse import urlparse
from threading import Thread
from hashlib import sha1
from random import randint, randbytes
import time
import socket
import math
import copy

LISTENING_PORT_START = 6881
CONNECTION_TIMEOUT   = 5

class Client:

    def __init__(self, listening_socket, 
                transaction_id, peer_id, port,
                downloaded, left, uploaded):

        self.listening_socket = listening_socket
        self.transaction_id   = transaction_id 
        self.peer_id          = peer_id 
        self.port             = port
        self.downloaded       = downloaded
        self.left             = left
        self.uploaded         = uploaded


def get_tcp_socket():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return tcp_socket

def get_file_list(info):
    if b'files' not in info:
        file_name = info[b'name']
        file_length = info[b'length']
        return [(file_name, file_length)]
    else:
        file_list = []
        for file in info[b'files']:
            file_length = file[b'length']
            file_name = name + "/" + (b'/'.join(file[b'path'])).decode()
            file_list.append((file_name, file_length))
        return file_list


def get_listening_socket():
    listening_socket = get_tcp_socket()
    port = LISTENING_PORT_START
    while(True):
        try:
            listening_socket.bind(('', port))
        except socket.error as sock_error:
            if(sock_error.errno == errno.EADDRINUSE):
                port += 1
            else:
                raise
        else:
            break

    return listening_socket

def initialize_pieces(total_size, piece_length, pieces_sha1):
    print("piece length", piece_length)
    pieces = Pieces()
    piece_count = math.ceil(total_size / piece_length)
    last_piece_length = total_size % piece_length

    for index in range(piece_count):
        sha1_start = index * 20
        if(index == piece_count - 1):
            piece = Piece(index, last_piece_length, 
                        pieces_sha1[sha1_start:sha1_start + 20])
        else:
            piece = Piece(index, piece_length, 
                        pieces_sha1[sha1_start:sha1_start + 20])
        pieces.append(piece)

    return pieces



udp_announce_response_names = [
        "action", 
        "transaction_id", 
        "interval", 
        "leechers",
        "seeders",
        "peers"
    ]

http_announce_response_names = [
        "seeders",
        "leechers",
        "interval",
        "peers"
    ]

#read the bit torrent file from the command line
#FILE PARSING
def main(torrent_file, peer_limit):
    bdecoder =  Bdecoder(torrent_file, "f")
    bencoder = Bencoder()
    decoded_torrent_file = bdecoder.decode()[0]
    info = decoded_torrent_file[b'info']

    #FILE OPENING
    file_list = get_file_list(info)
    file_array = FileArray(file_list, info[b'piece length'])

    #GLOBALS
    listening_socket         = get_listening_socket()
    listening_socket_address = listening_socket.getsockname()

    announce_url = decoded_torrent_file[b'announce'].decode()
    info_hash    = sha1(bencoder.bencode(info)).digest()
    client       = Client(listening_socket, randint(1, 1 << 31 - 1), 
                        randbytes(PEER_ID_SIZE), listening_socket_address[1], 
                        0, file_array.total_size, 0)

    #ANNOUNCING
    url_parse_object = urlparse(announce_url)

    tracker_type      = None
    tracker           = None

    announce_response_dictionary = {}

    tracker_url = url_parse_object.geturl()
    print(tracker_url)

    if(url_parse_object.scheme == 'http' or url_parse_object.scheme == 'https'):
        tracker_type = 'http'
        tracker = httprequest.HTTPRequest(tracker_url)
        announce_response = tracker.announce(info_hash, client.peer_id, 
                client.downloaded, client.left,
                client.uploaded, client.port)
        announce_decoder = Bdecoder(announce_response, "b")
        announce_response_bdictionary = announce_decoder.decode()[0]
        for key, value in announce_response_bdictionary.items():
            if(key == b'peers'):
                announce_response_dictionary[key.decode()] = value
            else:
                announce_response_dictionary[key.decode()] = int(value)

    else:
        tracker_type = 'udp'
        tracker = udprequest.UDPRequest(tracker_url)
        action, transaction_id, connection_id = tracker.connect(client.transaction_id)
        key = randint(1, 1 << 31 - 1)
        announce_response = tracker.announce(connection_id, client.transaction_id,
                info_hash, client.peer_id, 
                client.downloaded, client.left, 
                client.uploaded, client.port, 
                key)
        announce_response_dictionary = dict(zip(announce_response_names,
                                                announce_response))

    peer_address_list = parse_compact_peers(announce_response_dictionary["peers"])

    piece_length = info[b'piece length']
    torrent_pieces = initialize_pieces(file_array.total_size, piece_length, info[b'pieces'])

    peer_list = []
    print("connecting peer")
    for peer_address in peer_address_list:
        if(not peer_limit):
            break
        print(peer_address)
        peer_socket = get_tcp_socket()
        peer_socket.settimeout(CONNECTION_TIMEOUT)
        try:
            peer_socket.connect(peer_address)
        except (socket.timeout, OSError):
            continue
        peer = Peer(peer_socket, copy.deepcopy(torrent_pieces))
        peer_list.append(peer)
        peer_limit -= 1

    print("creating torrent object")
    torrent = Torrent(file_array, client.peer_id, peer_list, info_hash,
                    torrent_pieces)

    print('handing peers')
    peer_threads = []
    for peer in peer_list:
        peer_thread = Thread(target=handle_peer, args=(peer, torrent))
        peer_thread.start()
        peer_threads.append(peer_thread)

    print('unchoking peers')
    torrent.unchoke_top_peers()
    '''
    peer_unchoking_scheduler = sched.scheduler(time.time, time.sleep)
    peer_unchoking_scheduler.enter(60, unchoke_peers, arguments=(torrent,))
    peer_unchoking_scheduler.run()
    '''

    #time.sleep(2)
    #torrent.torrent_status = TorrentStatus.STOPPED
        #create torrent object
        #TODO create listening thread
    #start_listening(listening_socket, torrent)
        #schedule the sorting of peer and chocking/unchocking based on the download
        #speed
        #send interested to the each peer
        #handle each peer


if __name__ == "__main__":
        torrent_file = ("./research/torrentfile/ubuntu-21.04-desktop-amd64.iso.torrent")
        main(torrent_file, 4)



