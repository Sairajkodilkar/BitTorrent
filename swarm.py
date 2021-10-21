
def handel_peer(peer:Peer, torrent:Torrent):
    peer.handshake()
    create reving thread
    continue to send from here
    initialize the request queue
    while sending go from state to state 
        if(he is not alive abort):
        if(i he is unchoked and he is interested):
            send the torrent
        else if(he is interested and unchoked):
            then unchoke him as per master thread
        if(request queue is not empty):
            serve requests

    while recving:
        keep on recving and updating the states
        update the state as uploading
        if valid checsm then hold the "block" in the buffer 
        if the block is completed then simply write it to the 
        if request then simply write the request to the request queueu
        after recving validate the checksum of the piece
        update the block as completed 
        write it to the file
