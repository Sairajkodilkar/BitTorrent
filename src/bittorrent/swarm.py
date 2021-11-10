from bittorrent.peers.packetization import ID, IndentityError
from bittorrent.torrent import TorrentStatus
from bittorrent.piece import Piece, PieceStatus

from threading import Thread, Event
import socket
import sched
import time

# This is not efficient
# every peer adds the overhead of 3 threads

# Note that these are 15 seconds smaller than the official time
KEEP_ALIVE_DATA_TIME = 20
KEEP_ALIVE_KEEP_TIME = 105

REQUEST_EVENT_TIMEOUT = 30

def cancel_all_events(scheduler):
    for event in scheduler.queue:
        scheduler.cancel(event)
    return


def send_scheduled_keep_alive(torrent, peer, keep_alive_scheduler):
    while(peer.connected):
        cancel_all_events(keep_alive_scheduler)
        if(torrent.data_sent):
            keep_alive_scheduler.enter(
                KEEP_ALIVE_DATA_TIME, 1, peer.keep_alive)
            torrent.data_sent = False
        else:
            keep_alive_scheduler.enter(
                KEEP_ALIVE_KEEP_TIME, 1, peer.keep_alive)
        try:
            keep_alive_scheduler.run()
        except ConnectionError:
            peer.close()
    return


def request_rarest_piece(torrent, peer, keep_alive_scheduler):
    for rarest_piece in sorted(torrent.pieces, reverse=True):
        if(rarest_piece.get_status() is None
                and peer.pieces[rarest_piece.index].piece_count):

            print(request_pieces, rarest_piece.index)
            torrent.data_sent = True
            cancel_all_events(keep_alive_scheduler)
            rarest_piece.request(peer)
            return
    return



def request_pieces(peer, torrent, keep_alive_scheduler, request_event):
    while(peer.connected and torrent.get_status() == TorrentStatus.LEECHER):
        if(request_event.wait(REQUEST_EVENT_TIMEOUT)
                and peer.i_am_interested and not peer.choked_me):

            request_rarest_piece(torrent, peer, keep_alive_scheduler)
            time.sleep(0.2)
    return


def clear_pieces_status(peer, torrent):
    for piece in peer.pieces:
        if (piece.get_status() != PieceStatus.COMPLETED
            and torrent.pieces[piece.index].get_status() != PieceStatus.COMPLETED):

            piece.set_status(None)
            torrent.pieces[piece.index].set_status(None)
            torrent.pieces[piece.index].discard_data()
    return


def send_block(torrent, peer, index, begin, length):
    block = torrent.data_files.read_block(index, begin, length)
    try:
        peer.send_block(index, begin, block)
    except ConnectionError:
        peer.close()
    return


def send_have(torrent, peer):

    for piece in torrent.pieces:
        if(piece.get_status() == PieceStatus.COMPLETED and
                peer.pieces[piece.index].get_status() != PieceStatus.COMPLETED):
            peer.have(piece.index)
    return


def send_scheduled_have(torrent, peer):
    have_scheduler = sched.scheduler(time.time, time.sleep)
    while(peer.connected):
        have_scheduler.enter(5, 1, send_have, argument=(torrent, peer))
        have_scheduler.run()
    return

EXTENDED = 0x0000000000100000
FAST_EXTENSION = 0x0000000000000004

def handle_peer(peer, torrent):

    torrent.data_sent = False
    try:
        peer.set_timeout(REQUEST_EVENT_TIMEOUT)
    except OSError:
        peer.close()
        return

    handshake_response = None
    try:
        handshake_response = peer.send_handshake(
            torrent.info_hash, torrent.peer_id, reserved=0)
    except socket.timeout:
        peer.close()
        return
    except (ConnectionError, OSError):
        peer.close()
        return


    if(handshake_response[3] != torrent.info_hash):
        peer.close()
        return

    bitfield = torrent.pieces.get_bitfield()
    peer.send_bitfield(bitfield)

    peer.interested(True)
    keep_alive_scheduler = sched.scheduler(time.time, time.sleep)

    keep_alive_thread = Thread(target=send_scheduled_keep_alive,
                               args=(torrent, peer, keep_alive_scheduler))
    keep_alive_thread.setDaemon(True)
    keep_alive_thread.start()

    request_event = Event()
    request_thread = Thread(target=request_pieces, args=(peer, torrent,
                                                         keep_alive_scheduler,
                                                         request_event))
    request_thread.setDaemon(True)
    request_thread.start()

    send_scheduled_have_thread = Thread(
        target=send_scheduled_have, args=(torrent, peer))
    send_scheduled_have_thread.setDaemon(True)
    send_scheduled_have_thread.start()

    while(peer.connected and torrent.get_status() != TorrentStatus.STOPPED):

        try:
            message = peer.recv_all()
        except (socket.timeout, ConnectionResetError, OSError) as s:
            peer.close()
            break
        except IndentityError:
            continue

        if(message[0] == -1):
            continue
            peer.close()

        elif(message[0] == ID.CHOKE):
            request_event.clear()

        elif(message[0] == ID.UNCHOKE):
            request_event.set()

        elif(message[0] == ID.INTERESTED):
            continue

        elif(message[0] == ID.BIT_FIELD):
            torrent.pieces.add_bitfield(message[1])

        elif(message[0] == ID.REQUEST):
            if(peer.choked or not peer.interested_in_me):
                continue
            if(message[3] > Piece.MAX_BLOCK_SIZE):
                continue
            if(torrent.pieces[message[1]].get_status() != PieceStatus.COMPLETED):
                continue
            send_block(torrent, peer, message[1], message[2], message[3])
            torrent.data_sent = True
            cancel_all_events(keep_alive_scheduler)

        elif(message[0] == ID.PIECE):
            if(torrent.pieces[message[1]].get_status() == PieceStatus.COMPLETED):
                continue
            tpiece = torrent.pieces[message[1]]
            ppiece = peer.pieces[message[1]]
            ppiece.set_status(PieceStatus.DOWNLOADING)
            tpiece.add_block(message[2], message[3])
            if(tpiece.get_status() == PieceStatus.COMPLETED):
                ppiece.set_status(PieceStatus.COMPLETED)
                torrent.data_files.write_block(tpiece.index, 0, tpiece.data)
                tpiece.discard_data()

        elif(message[0] == ID.HAVE):
            # this condition is already handled in the peer 
            continue

        elif(message[0] == ID.CANCEL):
            continue

        elif(message[0] == ID.EXTENDED):
            # ignore the bittorrent extension message as they are not useful
            # now
            continue

        elif(message[0] == ID.HAVE_ALL):
            peer.have_none()
            continue 

        elif(message[0] == ID.PORT):
            # useful in DHT
            pass
        else:
            # for now ignore such messages
            pass

        try:
            if(message[0] == ID.KEEP_ALIVE):
                peer.set_timeout(120)
            else:
                peer.set_timeout(30)
        except OSError:
            peer.close()

    cancel_all_events(keep_alive_scheduler)
    clear_pieces_status(peer, torrent)
    peer.close()
    return
