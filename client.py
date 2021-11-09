from bittorrent.bdencoder.bdencoder import Bdecoder, Bencoder 
from bittorrent.bdencoder.bdencoder import BdecodingError, BencodingError 
from bittorrent.peers.peer import Peer, PEER_ID_SIZE
from bittorrent.torrent import Torrent, TorrentStatus
from bittorrent.request import httprequest, udprequest
from bittorrent.fileio import FileArray
from bittorrent.swarm import handle_peer, cancel_all_events
from bittorrent.parse import parse_compact_peers, parse_scrape_res
from bittorrent.piece import Piece, Pieces, PieceStatus
from bittorrent.user import display_status

from random import randint, randbytes
from urllib.parse import urlparse
from threading import Thread
from hashlib import sha1
import os
import sys
import time
import math
import copy
import sched
import errno
import socket
import signal
LISTENING_PORT_START = 6881
CONNECTION_TIMEOUT = 1


class Client:

    def __init__(self, listening_socket, info_hash,
                 transaction_id, peer_id, port,
                 downloaded, left, uploaded,
                 piece_count, seeding):

        self.listening_socket = listening_socket
        self.info_hash = info_hash
        self.transaction_id = transaction_id
        self.peer_id = peer_id
        self.port = port
        self.downloaded = downloaded
        self.left = left
        self.uploaded = uploaded
        self.piece_count = piece_count
        self.seeding = seeding


def get_tcp_socket():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return tcp_socket


def get_file_list(info, basedir):
    if(basedir and basedir[-1] != "/"):
        basedir += "/"
        if(not os.path.exists(basedir)):
            raise Exception(f"{basedir} does not exists")
        if(not os.path.isdir(basedir)):
            raise Exception(f"{basedir} is not a directory")
    if b'files' not in info:
        file_name = basedir + info[b'name'].decode()
        file_length = info[b'length']
        return [(file_name, file_length)]
    else:
        file_list = []
        for file in info[b'files']:
            file_length = file[b'length']
            file_name = basedir + info[b'name'].decode() + "/" + \
                (b'/'.join(file[b'path'])).decode()
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


def schedule_unchoke(torrent, peer_unchoking_scheduler, peer_unchoke_limit):
    while(torrent.get_status() != TorrentStatus.STOPPED):
        peer_unchoking_scheduler.enter(30, 1, torrent.unchoke_top_peers,
                                       argument=(peer_unchoke_limit, ))
        peer_unchoking_scheduler.run()
    return


def initialize_pieces(total_size, piece_length, pieces_sha1):
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


def start_listening(listening_socket, torrent, pieces, peer_threads):
    # set the timeout to 10 seconds so that we can check for stop condition
    listening_socket.settimeout(10)
    listening_socket.listen(10)
    while(torrent.get_status() != TorrentStatus.STOPPED):
        try:
            conn, address = listening_socket.accept()
        except socket.timeout:
            continue
        peer = Peer(conn, copy.deepcopy(pieces))
        peer_thread = Thread(target=handle_peer, args=(peer, torrent))
        peer_thread.start()
        peer_threads.append(peer_thread)
        torrent.peers.append(peer)
    return


def get_announce_response(tracker_url, client):
    url_parse_object = urlparse(tracker_url)
    announce_response_dictionary = {}

    if(url_parse_object.scheme == 'http' or url_parse_object.scheme == 'https'):
        tracker = httprequest.HTTPRequest(tracker_url)

        announce_response = tracker.announce(client.info_hash, client.peer_id,
                                             client.downloaded, client.left,
                                             client.uploaded, client.port,
                                             num_want=50)

        announce_decoder = Bdecoder(announce_response, "b")
        announce_response_bdictionary = announce_decoder.decode()[0]
        for key, value in announce_response_bdictionary.items():
            if(key == b'peers'):
                announce_response_dictionary[key.decode()] = value
            else:
                announce_response_dictionary[key.decode()] = int(value)
    else:
        tracker = udprequest.UDPRequest(tracker_url)
        try:
            action, transaction_id, connection_id = tracker.connect(
                client.transaction_id)
        except socket.timeout:
            raise
        key = randint(1, 1 << 31 - 1)
        announce_response = tracker.announce(connection_id, client.transaction_id,
                                             client.info_hash, client.peer_id,
                                             client.downloaded, client.left,
                                             client.uploaded, client.port,
                                             key, num_want=50)
        announce_response_dictionary = dict(zip(udprequest.UDP_ANNOUNCE_RESPONSE_NAMES,
                                                announce_response))
    return announce_response_dictionary


def verify_file(file_array, torrent_pieces):
    downloaded = 0
    for i in range(len(torrent_pieces)):
        piece = file_array.read_block(i, 0, file_array.piece_length)
        if(not piece):
            # no more data in file
            break
        piece_sha1 = sha1(piece).digest()
        if(piece_sha1 == torrent_pieces[i].sha1):
            print("matched the data", i)
            downloaded += len(torrent_pieces[i])
            torrent_pieces.add_piece(i)
        else:
            continue
    return downloaded


def download(torrent_file, peer_connection_limit=20, peer_unchoke_limit=5,
             basedir='', clean_download=False, seeding=False):
    # Decoding the torrent files
    print("Decoding torrent file...")

    bdecoder = Bdecoder(torrent_file, "f")
    bencoder = Bencoder()

    decoded_torrent_file = None
    try:
        decoded_torrent_file = bdecoder.decode()[0]
    except BdecodingError as bde:
        print(f"{torrent_file} is not a valid torrent file")

    info = decoded_torrent_file[b'info']

    # File opening
    try:
        file_list = get_file_list(info, basedir)
    except Exception as e:
        print(e)
        sys.exit(1)

    file_array = FileArray(file_list, info[b'piece length'])

    # Initialize the Pieces
    piece_length = info[b'piece length']
    torrent_pieces = initialize_pieces(
        file_array.total_size, piece_length, info[b'pieces'])
    peer_pieces = copy.deepcopy(torrent_pieces)

    downloaded = 0

    if(not clean_download):
        print("Checking for Downloaded data...")

        downloaded = verify_file(file_array, torrent_pieces)
    if(seeding and downloaded != file_array.total_size):
        print("Cant seed the torrent")
        print("It may be Incomplete or Currupted..")

        file_array.close_all()
        sys.exit(1)

    left = file_array.total_size - downloaded
    if(left == 0):
        print("File is completely downloaded")
        yn = print("Do you want to start seeding [y/n]?")

        if(yn[0] == 'y'):
            seeding = True
        else:
            file_array.close_all()
            sys.exit()

    uploaded = 0

    piece_count = math.ceil(file_array.total_size / piece_length)

    # Globals
    listening_socket = get_listening_socket()
    listening_socket_address = listening_socket.getsockname()
    info_hash = sha1(bencoder.bencode(info)).digest()
    client = Client(listening_socket, info_hash, randint(1, 1 << 31 - 1),
                    randbytes(PEER_ID_SIZE), listening_socket_address[1],
                    downloaded, left, uploaded, piece_count, seeding)

    if(b'announce-list' in decoded_torrent_file):
        announce_list = decoded_torrent_file[b'announce-list']
    else:
        announce_list = [[decoded_torrent_file[b'announce']]]

    peer_address_list = []

    print("Connecting to the tracker...")

    while(not peer_address_list):
        loops = 0
        for tracker_url in announce_list:
            try:
                announce_response_dictionary = get_announce_response(
                    tracker_url[0].decode(), client)
            except:
                continue
            if("failure" in announce_response_dictionary):
                print("Failed to fetch the torrentServer sent" +
                      announce_response_dictionary["failure"] + "")
                print("Aborting")

                file_array.close_all()
                return
            if(client.seeding):
                break
            if("peers" in announce_response_dictionary):
                peer_address_list += parse_compact_peers(
                    announce_response_dictionary["peers"])
                print("Got list of peers from " +
                      tracker_url[0].decode() + "")
            else:
                print("Tracker " + tracker_url[0].decode() +
                      " gave 0 peers")

        if(client.seeding):
            break

        # TODO: handel failure
        # Try continuously till 5 loops and wait for 10 seconds
        if(loops > 5):
            loops = 0
            print("Tracker is not responding")
            print("Will try contacting tracker in 10 seconds")

            time.sleep(10)
        loops += 1
        # Wait for the interval specified by the tracker to ping
        if(not peer_address_list):
            interval = announce_response_dictionary["interval"]
            time.sleep(interval)

    # Generate the peer list
    print("Connecting to the peers")

    peer_list = []
    for peer_address in peer_address_list:
        if(client.seeding):
            break
        if(not peer_connection_limit):
            break
        peer_socket = get_tcp_socket()
        peer_socket.settimeout(CONNECTION_TIMEOUT)
        try:
            peer_socket.connect(peer_address)
        except (socket.timeout, OSError):
            continue
        # deepcopy ensures that each peer get its own pieces array
        peer = Peer(peer_socket, copy.deepcopy(peer_pieces))
        peer_list.append(peer)
        peer_connection_limit -= 1

    # Create the globally used torrent object
    # This object is use for communication across all the peers
    torrent = Torrent(file_array, client.peer_id, peer_list, info_hash,
                      copy.deepcopy(torrent_pieces))

    if(client.seeding):
        torrent.set_status(TorrentStatus.SEEDER)
    # Create the thread for each peer
    peer_threads = []
    print("Downloading torrent")

    for peer in peer_list:
        peer_thread = Thread(target=handle_peer, args=(peer, torrent))
        peer_thread.start()
        peer_threads.append(peer_thread)

    # Wait for handshakes to complete
    time.sleep(5)
    torrent.unchoke_top_peers(peer_unchoke_limit)

    # Schedule the unchoking of the top leechers
    peer_unchoking_scheduler = sched.scheduler(time.time, time.sleep)
    scheduled_unchoke_thread = Thread(target=schedule_unchoke,
                                      args=(torrent, peer_unchoking_scheduler, peer_unchoke_limit))
    scheduled_unchoke_thread.start()

    # Start listening for the incoming connections
    listening_thread = Thread(target=start_listening, args=(listening_socket,
                                                            torrent,
                                                            torrent_pieces,
                                                            peer_threads))
    listening_thread.start()

    def signal_handler(signum, frame):
        torrent.set_status(TorrentStatus.STOPPED)
        cancel_all_events(peer_unchoking_scheduler)
        print()
        print("Closing Torrent.. Wait few seconds")
        return

    signal.signal(signal.SIGINT, signal_handler)

    # User interface
    display_status(client, torrent, peer)

    file_array.close_all()
