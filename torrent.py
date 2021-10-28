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
from piece import Status, Piece, Pieces
from bittorrent.fileio import File

class TorrentStatus:
    LEECHER = 1
    SEEDER = 2

class Torrent:

    def __init__(self, data_file:File, peer_id:bytes, peers:list,
            info_hash:bytes,
            pieces:Pieces, torrent_status=TorrentStatus.LEECHER):

        self.data_file      = data_file 
        self.peers          = peers
        self.peer_id        = peer_id
        self.info_hash      = info_hash
        self.torrent_status = torrent_status
        self.pieces         = pieces
        #schedule sorting after every 1 min

    def _sort_peers(self):
        if(self.torrent_status ==  TorrentStatus.LEECHER):
            self.peers.sort(key=Peers.get_download_speed, reverse=True)
        else:
            self.peers.sort(key=Peers.get_upload_speed, reverse=True)

    def add_peers(self, peers):
        self.peers.append(peers)

    @property
    def completed(self):
        if(self.torrent_status == TorrentStatus.SEEDER):
            return True
        for piece in self.pieces:
            if(piece.status != Status.COMPLETED):
                return False
        self.torrent_status = TorrentStatus.SEEDER
        return True
