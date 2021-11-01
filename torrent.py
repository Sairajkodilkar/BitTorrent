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
from bittorrent.fileio import File
from bittorrent.piece import Status, Piece, Pieces
from bittorrent.fileio import FileArray
from bittorrent.peers.peer import Peer
from random import randint

class TorrentStatus:
    LEECHER = 1
    SEEDER  = 2
    STOPPED = 3

class Torrent:

    def __init__(self, data_files:FileArray, peer_id:bytes, peers:list,
            info_hash:bytes,
            pieces:Pieces, torrent_status=TorrentStatus.LEECHER, peer_limit=5):

        self.data_files     = data_files
        self.peers          = peers
        self.peer_id        = peer_id
        self.info_hash      = info_hash
        self.torrent_status = torrent_status
        self.pieces         = pieces
        self.peer_limit     = peer_limit
        self.unchoked_peers = []
        #schedule sorting after every 1 min

    def _sort_unchoked_peers(self):
        if(self.torrent_status ==  TorrentStatus.LEECHER):
            self.unchoked_peers.sort(key=Peer.get_download_speed, reverse=True)
        else:
            self.unchoked_peers.sort(key=Peer.get_upload_speed, reverse=True)

    def unchoke_top_peers(self):
        if(not self.unchoked_peers):
            peer_range = min(len(self.peers), self.peer_limit)
            for i in range(peer_range):
                peer = self.peers.pop()
                peer.choke(False)
                self.unchoked_peers.append(peer)
        else:
            self._sort_unchoked_peers()

            slowest_peer = self.unchoked_peers.pop()
            slowest_peer.choke(True)
            self.peers.append(slowest_peer)

            random_peer_index = randint(0, len(self.peers) - 1)
            random_peer = self.peers.pop(random_peer_index)
            random_peer.choke(False)
            self.unchoked_peers.append(random_peer)


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

    def get_complete_piece_count(self):
        count = 0
        for piece in self.pieces:
            if(piece.status == Status.COMPLETED):
                count += 1
        return count


