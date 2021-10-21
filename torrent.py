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
class TorrentStatus:
    LEECHER = 1
    SEEDER = 2

class Torrent:

    def __init__(self, peer_id, peers_list, info_hash,
                no_of_pieces, torrent_status=TorrentStatus.LEECHER):

        self.peer_list      = peer_list
        self.peer_id        = peer_id
        self.info_hash      = info_hash
        self.torrent_status = torrent_status
        self.pieces_info    = pieces_info

    def get_completed_pieces(self):
        return bitfield

    def sort_peer_list(self):
        #the return list would be useful for rareest first
        pass
not 
    def update_torrent_bitfield(self, bitfield):
        pass

    def add_peers(self, peer_list):
        self.peer_list.append(peer_list)

    def update_piece_status(self, piece_index, status_id, status):
        pass

    def update_peer_status(self, peer_address, status_id, status):
        pass

    def get_piece_status(self, piece_index):
        pass

    def get_top_four(self):
        pass

    def is_torrent_completed(self):
        pass
