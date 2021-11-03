from bittorrent.peers.packetization import ID
from bittorrent.torrent import TorrentStatus
from bittorrent.piece import Pieces, Piece, PieceStatus

from threading import Thread, Event
import socket
import sched
import time
import sys

#This is not efficient 
#every peer adds the overhead of 3 threads

#Note that these are 15 seconds smaller than the official time
KEEP_ALIVE_DATA_TIME = 20
KEEP_ALIVE_KEEP_TIME = 20

REQUEST_EVENT_TIMEOUT = 30


def cancel_all_events(keep_alive_scheduler):
    for event in keep_alive_scheduler.queue:
        keep_alive_scheduler.cancel(event)
    return

def send_scheduled_keep_alive(torrent, peer, keep_alive_scheduler):
    while(peer.connected):
        cancel_all_events(keep_alive_scheduler)
        if(torrent.data_sent):
            keep_alive_scheduler.enter(KEEP_ALIVE_DATA_TIME, 1, peer.keep_alive)
            torrent.data_sent = False
        else:
            keep_alive_scheduler.enter(KEEP_ALIVE_KEEP_TIME, 1, peer.keep_alive)
        try:
            keep_alive_scheduler.run()
        except ConnectionError:
            print("connection error")
            peer.close()
    print('exiting send', peer.connected, torrent.get_status())
    return

def request_rarest_piece(torrent, peer, keep_alive_scheduler):
    #for rarest_piece in sorted(torrent.pieces, reverse=True): 
    for rarest_piece in sorted(torrent.pieces, reverse=True): 
        if(rarest_piece.get_status() == None 
                and peer.pieces[rarest_piece.index].piece_count): 

            #print("requesting piece", rarest_piece.index)
            torrent.data_sent = True 
            cancel_all_events(keep_alive_scheduler) 
            rarest_piece.request(peer)
            #print(rarest_piece.status)
            return

def clear_pieces_status(peer, torrent):
    for piece in peer.pieces:
        if(piece.get_status() != PieceStatus.COMPLETED 
                and torrent.pieces[piece.index].get_status() != PieceStatus.COMPLETED):

            #print("clearing", piece.index)
            piece.set_status(None)
            torrent.pieces[piece.index].set_status(None)
            torrent.pieces[piece.index].discard_data()

def request_pieces(peer, torrent, keep_alive_scheduler, request_event):
    #TODO: refactor it
    while(peer.connected and torrent.get_status() == TorrentStatus.LEECHER):

        if(request_event.wait(REQUEST_EVENT_TIMEOUT) 
            and peer.i_am_interested and not peer.choked_me):

            #print("requesting")
            request_rarest_piece(torrent, peer, keep_alive_scheduler)
            time.sleep(0.2)
    return

def send_block(torrent, peer, index, begin, length):
    block = torrent.data_files.read_block(index, begin, length)
    try:
        peer.send_block(index, begin, block)
    except ConnectionError:
        print("send block failed")
        peer.close()
    return

def send_have(torrent, peer):

    for piece in torrent.pieces:
        if(peer.pieces[piece.index].piece_count == 0):
            peer.have(piece.index)
    return

def send_scheduled_have(torrent, peer):
    have_scheduler = sched.scheduler(time.time, time.sleep)
    while(peer.connected):
        have_scheduler.enter(15, 1, send_have, argument=(torrent, peer))
        have_scheduler.run()
    return

def handle_peer(peer, torrent):

    torrent.data_sent = False
    peer.set_timeout(REQUEST_EVENT_TIMEOUT)
    print("handling peer")

    handshake_response = None
    try:
        handshake_response = peer.send_handshake(torrent.info_hash, torrent.peer_id)
    except socket.timeout:
        print("timeout")
        peer.close()
        return
    except ConnectionError:
        print("connection error")
        peer.close()
        return

    if(handshake_response[3] != torrent.info_hash):
        print("info hash did not matched")
        peer.close()
        return

    bitfield = torrent.pieces.get_bitfield()
    peer.send_bitfield(bitfield)
    #TODO testing code, remove it
    peer.choke(False)

    #print("sending interested")
    peer.interested(True)
    keep_alive_scheduler = sched.scheduler(time.time, time.sleep)

    keep_alive_thread = Thread(target=send_scheduled_keep_alive, 
                                args=(torrent, peer, keep_alive_scheduler))
    keep_alive_thread.start()

    request_event = Event()
    request_thread = Thread(target=request_pieces, args=(peer, torrent, 
                                        keep_alive_scheduler, request_event))
    request_thread.start()

    send_scheduled_have_thread = Thread(target=send_scheduled_have, args=(torrent, peer))
    send_scheduled_have_thread.start()

    #print("starting main loop")
    while(peer.connected and torrent.get_status() != TorrentStatus.STOPPED):

        if(torrent.get_status() == TorrentStatus.SEEDER):
            raise Exception("Torrent is completed now")

        try:
            message = peer.recv_all()
        except (socket.timeout, ConnectionResetError, OSError):
            print("socket timeout")
            #print("conn reset")
            peer.close()
            break

        if(message[0] == -1):
            print("message -1")
            peer.close()

        elif(message[0] == ID.CHOCK):
            print("Choked")
            request_event.clear()

        elif(message[0] == ID.UNCHOCK):
            request_event.set()

        elif(message[0] == ID.INTERESTED):
            continue

        elif(message[0] == ID.BIT_FIELD):
            #print('adding bitfield')
            torrent.pieces.add_bitfield(message[1])
            c = 0
            for p in torrent.pieces:
                if(p.piece_count):
                    c += 1
            print("bitfield count", len(torrent.pieces), c)


        elif(message[0] == ID.REQUEST):
            print("request arrived")
            if(peer.choked or not peer.interested_in_me):
                print("aborting 1")
                continue
            if(message[3] > Piece.MAX_BLOCK_SIZE):
                print("aborting 2")
                continue
            if(torrent.pieces[message[1]].get_status() != PieceStatus.COMPLETED):
                print('aborting 3', torrent.pieces[message[1]].get_status())
                continue
            print("serving request")
            send_block(torrent, peer, message[1], message[2], message[3])
            print("request served")
            torrent.data_sent = True
            cancel_all_events(keep_alive_scheduler)

        elif(message[0] == ID.PIECE):
            #print("recved block", message[1], message[2], file=sys.stderr)
            if(torrent.pieces[message[1]].get_status() == PieceStatus.COMPLETED):
                #print("recved again", message[1])
                continue
            tpiece = torrent.pieces[message[1]]
            ppiece = peer.pieces[message[1]]
            ppiece.set_status(PieceStatus.DOWNLOADING)
            tpiece.add_block(message[2], message[3])
            if(tpiece.get_status() == PieceStatus.COMPLETED):
                ppiece.set_status(PieceStatus.COMPLETED)
                torrent.data_files.write_block(tpiece.index, 0, tpiece.data)
                tpiece.discard_data()
                #print("this is completed", ppiece.status == PieceStatus.COMPLETED, message[1], torrent.pieces[message[1]].status)

        elif(message[0] == ID.HAVE):
            torrent.pieces[message[1]].piece_count += 1
            peer.pieces[message[1]].piece_count += 1

        elif(message[0] == ID.CANCEL):
            continue

        elif(message[0] == ID.PORT):
            #useful in DHT
            pass
        else:
            #for now ignore such messages
            pass

        try:
            if(message[0] == ID.KEEP_ALIVE):
                peer.set_timeout(120)
            else:
                peer.set_timeout(30)
        except OSError:
            #print("os error", peer.peer_sock.getpeername())
            peer.close()

    cancel_all_events(keep_alive_scheduler)
    clear_pieces_status(peer, torrent)
    #print(torrent.pieces[0].status)
    #print("peer closed", peer.peer_sock.getpeername())
    return
