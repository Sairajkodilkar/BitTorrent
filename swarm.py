from bittorrent.peers.packetization import ID
from piece import Pieces, Piece, Status
from threading import Thread, Event
import sched
import time

#This is not efficient 
#every peer adds the overhead of 3 threads

#Note that these are 15 seconds smaller than the official time
KEEP_ALIVE_DATA_TIME = 20
KEEP_ALIVE_KEEP_TIME = 105

REQUEST_EVENT_TIMEOUT = 30

data_sent = False

def cancel_all_events(keep_alive_scheduler):
    for event in keep_alive_scheduler.queue:
        keep_alive_scheduler.cancel(event)
    return

def send_scheduled_keep_alive(peer, keep_alive_scheduler):
    global data_sent
    while(True):
        cancel_all_events(keep_alive_scheduler)
        if(data_sent):
            keep_alive_scheduler.enter(KEEP_ALIVE_DATA_TIME, peer.keep_alive)
            data_sent = False
        else:
            keep_alive_scheduler.enter(KEEP_ALIVE_KEEP_TIME, peer.keep_alive)
        keep_alive_scheduler.run()
    return

def send_rarest_piece(torrent, peer, keep_alive_scheduler):
    for rarest_piece in sorted(torrent.pieces, reverse=True): 
        if(rarest_piece.status == None 
                and peer.pieces[rarest_piece.index].piece_count): 

            data_sent = True 
            cancel_all_events(keep_alive_scheduler) 
            rarest_piece.request(peer)
    return

def request_pieces(peer, torrent, keep_alive_scheduler, request_event):
    #TODO: refactor it
    global data_sent
    while(peer.connected and not torrent.completed):
        if(request_event.wait(REQUEST_EVENT_TIMEOUT) 
            and peer.i_am_interested and not peer.choked_me):

            send_rarest_piece(torrent, peer, keep_alive_scheduler)
    return

def send_block(torrent, peer, index, begin, length):
        block = torrent.data_file.read_block(index, begin,length)
        try:
            peer.send_block(message[1], message[2], block)
        except ConnectionError:
            peer.close()
        return

def handle_peer(peer, torrent):

    handshake_response = peer.handshake(torrent.info_hash, torrent.peer_id)
    if(handshake_response[3] != torrent.info_hash):
        peer.close()
        return

    peer.set_timeout(30)

    keep_alive_scheduler = shed.scheduler(time.time, time.sleep)

    keep_alive_thread = Thread(target=send_scheduled_keep_alive, 
                                args=(peer, keep_alive_scheduler))
    keep_alive_thread.start()

    request_event = Event()
    request_thread = Thread(target=request_pieces, args=(peer, torrent, 
                                        keep_alive_scheduler, request_event))
    request_thread.start()

    while(peer.connected):

        try:
            message = peer.recv_all()
        except socket.timeout:
            peer.close()

        if(message[0] == -1):
            peer.close()

        elif(message[0] == ID.CHOCK):
            request_event.clear()

        elif(message[0] == ID.UNCHOCK):
            request_event.set()

        elif(message[0] == ID.INTERESTED):
            continue

        elif(message[0] == ID.BIT_FIELD):
            torrent.pieces.add_bitfield(message[1])

        elif(message[0] == ID.REQUEST 
            and not peer.chocked and peer.interested_in_me):
            if(message[3] > Piece.MAX_BLOCK_SIZE):
                continue
            if(not torrent.pieces[message[1]].completed):
                continue
            send_block(torrent, peer, message[1], message[2], message[3])

        elif(message[0] == ID.PIECE):
            piece = torrent.pieces[message[1]]
            piece.add_block(message[2], message[3])
            if(piece.status == Status.COMPLETED):
                torrent.data_file.write_piece(piece.index, piece.data)
                piece.discard_data()

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

        if(message[0] == ID.KEEP_ALIVE):
            peer.set_timeout(120)
        else:
            peer.set_timeout(30)

    return




