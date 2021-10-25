from collections import deque 
from bittorrent.peers.packetization import ID
from piece import Pieces, Piece
from threading import Thread

def request_pieces(peer, torrent):
    while(peer.connected):
        if(peer.interested and not peer.chocked_me):
            rarest_piece = torrent.get_rarest_piece()
            rarest_piece.request(peer)

def handle_peer(peer, torrent):

    handshake_response = peer.handshake(torrent.info_hash, torrent.peer_id)
    print(handshake_response)
    if(handshake_response[3] != torrent.info_hash):
        peer.close()
        return

    #request_thread = Thread(target=request_pieces, args=(peer, torrent))
    #request_thread.start()

    while(peer.connected):

        message = peer.recv_all()

        if(message[0] == -1):
            print("closing")
            peer.close()

        elif(message[0] == ID.REQUEST 
            and not peer.chocked and peer.interested_in_me):
            #TODO: use threading
            if(message[3] > Piece.MAX_BLOCK_SIZE):
                continue
            if(not torrent.pieces[message[1]].completed):
                continue
            block = torrent.data_file.read_block(message[1], message[2],
                                                message[3])
            try:
                peer.send_block(message[1], message[2], block)
            except ConnectionError:
                peer.close()

        elif(message[0] == ID.HAVE):
            torrent.pieces[message[1]].piece_count += 1
            peer.pieces[message[1]].piece_count += 1

        elif(message[0] == ID.PIECE):
            piece = torrent.pieces[message[1]]
            piece.add_block(message[2], message[3])
            if(piece.completed):
                torrent.data_file.write_piece(message[1], message[2],
                                            piece.data)
                piece.discard_data()

        elif(message[0] == ID.BIT_FIELD):
            torrent.pieces.add_bitfield(message[1])

        elif(message[0] == ID.CANCEL):
            pass

        elif(message[0] == ID.PORT):
            pass

        else:
            #for now ignore such messages
            pass

    return




