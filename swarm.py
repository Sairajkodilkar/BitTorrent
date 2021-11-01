from bittorrent.peers.packetization import ID
from bittorrent.piece import Pieces, Piece, Status
from threading import Thread, Event
from bittorrent.torrent import TorrentStatus
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

data_sent = False

def cancel_all_events(keep_alive_scheduler):
    for event in keep_alive_scheduler.queue:
        keep_alive_scheduler.cancel(event)
    return

def send_scheduled_keep_alive(torrent, peer, keep_alive_scheduler):
    global data_sent
    while(peer.connected and torrent.torrent_status != TorrentStatus.STOPPED):
        #cancel_all_events(keep_alive_scheduler)
        if(data_sent):
            keep_alive_scheduler.enter(KEEP_ALIVE_DATA_TIME, 1, peer.keep_alive)
            data_sent = False
        else:
            keep_alive_scheduler.enter(KEEP_ALIVE_KEEP_TIME, 1, peer.keep_alive)
        try:
            keep_alive_scheduler.run()
        except ConnectionError:
            clear_pieces_status(peer, torrent)
            peer.close()
    print('exiting send')
    return

def request_rarest_piece(torrent, peer, keep_alive_scheduler):
    #for rarest_piece in sorted(torrent.pieces, reverse=True): 
    for rarest_piece in sorted(torrent.pieces, reverse=True): 
        if(rarest_piece.status == None 
                and peer.pieces[rarest_piece.index].piece_count): 

            print("requesting piece", rarest_piece.index)
            data_sent = True 
            cancel_all_events(keep_alive_scheduler) 
            rarest_piece.request(peer)
    return

def clear_pieces_status(peer, torrent):
    for piece in peer.pieces:
        if(piece.status == Status.DOWNLOADING):
            print("clearing")
            pieces_status = Status.DOWNLOADING
            torrent.pieces[piece.index].status = None

def request_pieces(peer, torrent, keep_alive_scheduler, request_event):
    #TODO: refactor it
    global data_sent
    while(peer.connected and not torrent.completed and 
            torrent.torrent_status != TorrentStatus.STOPPED):
        if(request_event.wait(REQUEST_EVENT_TIMEOUT) 
            and peer.i_am_interested and not peer.choked_me):

            request_rarest_piece(torrent, peer, keep_alive_scheduler)
    return

def send_block(torrent, peer, index, begin, length):
        block = torrent.data_files.read_block(index, begin, length)
        try:
            peer.send_block(message[1], message[2], block)
        except ConnectionError:
            print("send block failed")
            peer.close()
        return


def handle_peer(peer, torrent):

    peer.set_timeout(REQUEST_EVENT_TIMEOUT)
    print("handling peer")

    handshake_response = None
    try:
        handshake_response = peer.send_handshake(torrent.info_hash, torrent.peer_id)
    except (socket.timeout, ConnectionError):
        print("timeout or connection error occured aborting")
        peer.close()
        return

    if(handshake_response[3] != torrent.info_hash):
        print("info hash did not matched")
        peer.close()
        return

    print("sending interested")
    peer.interested(True)
    keep_alive_scheduler = sched.scheduler(time.time, time.sleep)

    keep_alive_thread = Thread(target=send_scheduled_keep_alive, 
                                args=(torrent, peer, keep_alive_scheduler))
    keep_alive_thread.start()

    request_event = Event()
    request_thread = Thread(target=request_pieces, args=(peer, torrent, 
                                        keep_alive_scheduler, request_event))
    request_thread.start()

    print("starting main loop")
    while(peer.connected and torrent.torrent_status != TorrentStatus.STOPPED):

        if(torrent.completed == True):
            raise Exception("Torrent is completed now")

        peer.set_timeout(None)
        try:
            message = peer.recv_all()
        except (socket.timeout, ConnectionResetError):
            #print("socket timeout")
            peer.close()

        if(message[0] == -1):
            #print("message -1")
            peer.close()

        elif(message[0] == ID.CHOCK):
            request_event.clear()

        elif(message[0] == ID.UNCHOCK):
            request_event.set()

        elif(message[0] == ID.INTERESTED):
            continue

        elif(message[0] == ID.BIT_FIELD):
            print('adding bitfield')
            count = 0
            torrent.pieces.add_bitfield(message[1])
            for p in torrent.pieces:
                if(p.piece_count == 1):
                    count += 1
            print(count)

        elif(message[0] == ID.REQUEST):
            if(peer.chocked or not peer.interested_in_me):
                continue
            if(message[3] > Piece.MAX_BLOCK_SIZE):
                continue
            if(not torrent.pieces[message[1]].completed):
                continue
            send_block(torrent, peer, message[1], message[2], message[3])
            data_sent = True
            cancel_all_events(keep_alive_scheduler)

        elif(message[0] == ID.PIECE):
            print("recved block", message[1], message[2], file=sys.stderr)
            if(torrent.pieces[1].status == Status.COMPLETED):
                print("recved again")
                continue
            tpiece = torrent.pieces[message[1]]
            ppiece = peer.pieces[message[1]]
            ppiece.status = Status.DOWNLOADING
            tpiece.add_block(message[2], message[3])
            if(tpiece.status == Status.COMPLETED):
                print("this is completed", message[1], torrent.pieces[message[1]].status)
                ppiece.status = Status.COMPLETED
                torrent.data_files.write_block(tpiece.index, 0, tpiece.data)
                tpiece.discard_data()
                break

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
            peer.close()

    cancel_all_events(keep_alive_scheduler)
    clear_pieces_status(peer, torrent)
    print(torrent.pieces[0].status)
    print("peer closed")
    return




