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
from bittorrent.piece import PieceStatus, Piece, Pieces
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
            pieces:Pieces, status=TorrentStatus.LEECHER):

        self.peers          = peers
        self.pieces         = pieces

        self._data_files     = data_files
        self._peer_id        = peer_id
        self._info_hash      = info_hash
        self._status         = status
        self._unchoked_peers = []
        #schedule sorting after every 1 min

    def get_status(self):
        if(self._status == TorrentStatus.SEEDER
                or self._status == TorrentStatus.STOPPED):
            return self._status

        for piece in self.pieces:
            if(piece.get_status() != PieceStatus.COMPLETED):
                return TorrentStatus.LEECHER

        self._status = TorrentStatus.SEEDER
        return self._status

    def set_status(self, value):
        self._status = value
        return

    @property
    def peer_id(self):
        return self._peer_id

    @property
    def info_hash(self):
        return self._info_hash
    
    @property
    def data_files(self):
        return self._data_files

    def _sort_unchoked_peers(self):
        if(self._status ==  TorrentStatus.LEECHER):
            self._unchoked_peers.sort(key=Peer.get_download_speed, reverse=True)
        else:
            self._unchoked_peers.sort(key=Peer.get_upload_speed, reverse=True)

    def unchoke_top_peers(self, peer_limit=5):
        #TODO unchoke only when they are interested
        #This method will unchoke the seeders also which is not good
        if(not self._unchoked_peers):
            peer_range = min(len(self.peers), peer_limit)
            for i in range(peer_range):
                peer = self.peers.pop()
                peer.choke(False)
                self._unchoked_peers.append(peer)
        else:
            self._sort_unchoked_peers()

            slowest_peer = self._unchoked_peers.pop()
            slowest_peer.choke(True)
            self.peers.append(slowest_peer)

            random_peer_index = randint(0, len(self.peers) - 1)
            random_peer = self.peers.pop(random_peer_index)
            random_peer.choke(False)
            self._unchoked_peers.append(random_peer)
        print("unchoked len", len(self._unchoked_peers))

    def add_peers(self, peers):
        self.peers.append(peers)

    def get_completed_piece_count(self):
        count = 0
        for piece in self.pieces:
            if(piece.get_status() == PieceStatus.COMPLETED):
                count += 1
        return count
