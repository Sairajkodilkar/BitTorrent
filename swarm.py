from collections import deque 
import piece

def handel_peer(peer:Peer, torrent:Torrent):
    peer.handshake()
    create reving thread
    continue to send from here
    initialize the request queue
    set the timeout for the Peer

    #shedule the sending of the keep alives for the 
    #original thread
    #also set the idle timeout for the peer
    #if data recvd idle timeout is 30s
    #if keep alive recved the idle timeout is 120s
    while sending:
        if(he is not alive abort):
        if(he is unchoked and he is interested):
            send the torrent
        else if(he is interested and unchoked):
            then unchoke him as per master thread
        if(request queue is not empty):
            serve requests

    #recving thread
    while recving:
        keep on recving and updating the states
        update the state as uploading
        if valid checsm then hold the "block" in the buffer 
        if the block is completed then simply write it to the 
        if request then simply write the request to the request queueu
        Also check if the peer has timeout for the recving
        after recving validate the checksum of the piece
        update the block as completed 
        write it to the file

def send_peer(peer, torrent_piece): 
    start = 0 
    while(start < len(torrent_piece)):
        block_length = min(len(torrent_piece) - start, piece.MAX_BLOCK_SIZE) 
        block = piece.get_block(torrent_piece, start, length) 
        peer.send_block(block)
        start += block_length

def send_piece(peer, index, begin, length, lock):
    if(not peer.connected):
        return 
    #the lock is introduced to send the piece 
    lock.aquire()
    torrent_piece = torrent.data_file.read_piece(*request) 
    try: 
        send_entire_piece(peer, torrent_piece) 
    except ConnectionResetError: 
        peer.close()
    except:
        lock.release()
        raise

    lock.release()

    return

#what happens when the different thread calls the same function (e.g. send)
#master thread should choke unchoke interested not interested the peer
#recvr when encounter the request 

def handel_peer(peer, torrent):

    hanshake_response = peer.handshake(torrent.info_hash, torrent.peer_id)
    if(handshake_response[3] != torrent.info_hash):
        peer.close()
        return

    request_queue = deque()

    '''
    while(peer.connected):
        if(not peer.chock and peer.interested):
            while(request_queue):
               request = request_queue.popleft()

                   '''

    #reception
    while(peer.connected):
        message = peer.recv_all()
        if(message[0] == ID.REQUEST and not peer.chocked and peer.interested):
            #creating thread as the sending thread involves fileio overhead
            #threading will garrenty that the the piece is not used
            sending_thread = Thread((peer, message[1], message[2], message[3])


