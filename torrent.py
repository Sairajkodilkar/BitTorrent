#how to manage the peers
#connect to each peer
#each peer has to have bit field associated with it
#If I have 1 or more piece I need to send the bitfield to newly connected peer

#master thread will handel all the sending stuff 
#the recvr thread will recv and will change the state of all the 
#Peer Update should happen every 30 seconds


#The main thread will keep the torrent object and will pass this torrent object
#to the each peer thread it will create
#The main thread will sort the piece list every 1 min and the each torrent will
#the sorted list would be then used by the peer to determine the 
#peer handler will see if the corrosponding bit is turned on for the given peer 
#if yes it will request the piece from the that peer
#peer_list[peer]. I interested  and he unchock me then request
#peer_list[peer].he intertest and I unchocked him then simply serve the request
#                   else ignore the request
#each peer handler will have the sender and recvr thread where he will use FSM
from piece import Status, Piece

class TorrentStatus:
    LEECHER = 1
    SEEDER = 2

#TODO: create pieces class by inheriting the list class
#   Interface:
#       1) get_completed_pieces 
#       2) add_torrent_bitfield
#       3) add piece
class Torrent:

    def __init__(self, data_file:File, peer_id, peers, info_hash,
                pieces, torrent_status=TorrentStatus.LEECHER):

        self.data_file      = data_file 
        self.peers          = peers
        self.peer_id        = peer_id
        self.info_hash      = info_hash
        self.torrent_status = torrent_status
        self.pieces         = pieces
        #schedule sorting after every 1 min

    def _sort_peers(self):
        if(selt.torrent_status ==  TorrentStatus.LEECHER):
            self.peers.sort(key=Peers.get_download_speed, reverse=True)
        else:
            self.peers.sort(key=Peers.get_upload_speed, reverse=True)

    def get_rarest_piece(self):
        for piece in self.pieces:
            if(piece.piece_count and piece.status == None):
                return piece
        return 

    def add_peers(self, peers):
        self.peers.append(peers)

    def is_torrent_completed(self):
        for piece in self.pieces:
            if(piece.status != Status.COMPLETED):
                return False
        return True

    def get_completed_pieces(self):
        bitfield = 0
        currentbit = 1
        for piece in self.pieces:
            if piece.status == Status.COMPLETED:
                bitfield = bitfield | currentbit 
            currentbit = currentbit << 1
        total_pieces = len(self.pieces_list)
        total_bytes = total_pieces / 8 + total_pieces % 8
        bitfield_bytes = bitfield.to_bytes(total_bytes, "big")
        return bitfield






